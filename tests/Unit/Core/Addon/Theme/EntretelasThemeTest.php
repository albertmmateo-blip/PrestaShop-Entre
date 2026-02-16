<?php
/**
 * Copyright since 2007 PrestaShop SA and Contributors
 * PrestaShop is an International Registered Trademark & Property of PrestaShop SA
 *
 * NOTICE OF LICENSE
 *
 * This source file is subject to the Open Software License (OSL 3.0)
 * that is bundled with this package in the file LICENSE.md.
 * It is also available through the world-wide-web at this URL:
 * https://opensource.org/licenses/OSL-3.0
 * If you did not receive a copy of the license and are unable to
 * obtain it through the world-wide-web, please send an email
 * to license@prestashop.com so we can send you a copy immediately.
 *
 * DISCLAIMER
 *
 * Do not edit or add to this file if you wish to upgrade PrestaShop to newer
 * versions in the future. If you wish to customize PrestaShop for your
 * needs please refer to https://devdocs.prestashop.com/ for more information.
 *
 * @author    PrestaShop SA and Contributors <contact@prestashop.com>
 * @copyright Since 2007 PrestaShop SA and Contributors
 * @license   https://opensource.org/licenses/OSL-3.0 Open Software License (OSL 3.0)
 */

declare(strict_types=1);

namespace Tests\Unit\Core\Addon\Theme;

use PHPUnit\Framework\TestCase;
use PrestaShop\PrestaShop\Core\Addon\Theme\ThemeValidator;
use PrestaShop\PrestaShop\Core\ConfigurationInterface;
use Symfony\Component\Yaml\Parser;
use Symfony\Contracts\Translation\TranslatorInterface;

/**
 * Tests specific to the Entretelas theme to ensure:
 * 1. Theme structure is valid
 * 2. Font files are present and accessible
 * 3. CSS files reference correct font paths
 * 4. Theme configuration is valid
 */
class EntretelasThemeTest extends TestCase
{
    private const THEME_PATH = __DIR__ . '/../../../../../../themes/entretelas';

    /**
     * Test that the entretelas theme directory exists
     */
    public function testThemeDirectoryExists(): void
    {
        $this->assertDirectoryExists(self::THEME_PATH, 'Entretelas theme directory should exist');
    }

    /**
     * Test that theme.yml configuration file exists and is valid
     */
    public function testThemeConfigurationExists(): void
    {
        $configPath = self::THEME_PATH . '/config/theme.yml';
        $this->assertFileExists($configPath, 'Theme configuration file should exist');

        $parser = new Parser();
        $config = $parser->parseFile($configPath);

        $this->assertIsArray($config, 'Theme configuration should be valid YAML');
        $this->assertArrayHasKey('name', $config);
        $this->assertEquals('entretelas', $config['name']);
        $this->assertArrayHasKey('version', $config);
        $this->assertArrayHasKey('assets', $config);
    }

    /**
     * Test that custom CSS is enabled in theme configuration
     */
    public function testCustomCssIsEnabled(): void
    {
        $configPath = self::THEME_PATH . '/config/theme.yml';
        $parser = new Parser();
        $config = $parser->parseFile($configPath);

        $this->assertArrayHasKey('assets', $config);
        $this->assertArrayHasKey('css', $config['assets']);
        $this->assertArrayHasKey('all', $config['assets']['css']);

        $customCssFound = false;
        foreach ($config['assets']['css']['all'] as $cssAsset) {
            if ($cssAsset['id'] === 'entretelas-custom') {
                $customCssFound = true;
                $this->assertEquals('assets/css/custom.css', $cssAsset['path']);
                break;
            }
        }

        $this->assertTrue($customCssFound, 'Custom CSS should be enabled in theme configuration');
    }

    /**
     * Test that required font files exist in the correct location
     */
    public function testFontFilesExist(): void
    {
        $fontsPath = self::THEME_PATH . '/assets/css/fonts';
        $this->assertDirectoryExists($fontsPath, 'Fonts directory should exist');

        $pumpTridFont = $fontsPath . '/PumpTriD Regular.ttf';
        $quagmireFont = $fontsPath . '/Quagmire Extended Bold.otf';

        $this->assertFileExists($pumpTridFont, 'PumpTriD Regular.ttf font file should exist');
        $this->assertFileExists($quagmireFont, 'Quagmire Extended Bold.otf font file should exist');

        // Verify files are not empty
        $this->assertGreaterThan(0, filesize($pumpTridFont), 'PumpTriD font file should not be empty');
        $this->assertGreaterThan(0, filesize($quagmireFont), 'Quagmire font file should not be empty');
    }

    /**
     * Test that custom.css exists and contains proper font-face declarations
     */
    public function testCustomCssContainsFontFaceDeclarations(): void
    {
        $customCssPath = self::THEME_PATH . '/assets/css/custom.css';
        $this->assertFileExists($customCssPath, 'custom.css file should exist');

        $cssContent = file_get_contents($customCssPath);
        $this->assertNotEmpty($cssContent, 'custom.css should not be empty');

        // Check for PumpTriD font-face
        $this->assertStringContainsString('@font-face', $cssContent, 'custom.css should contain @font-face declarations');
        $this->assertStringContainsString('PumpTriD', $cssContent, 'custom.css should reference PumpTriD font');
        $this->assertStringContainsString('url(fonts/PumpTriD', $cssContent, 'custom.css should reference PumpTriD font file with correct path');

        // Check for Quagmire font-face
        $this->assertStringContainsString('Quagmire Extended', $cssContent, 'custom.css should reference Quagmire Extended font');
        $this->assertStringContainsString('url(fonts/Quagmire', $cssContent, 'custom.css should reference Quagmire font file with correct path');

        // Verify no references to broken Manrope fonts
        $this->assertStringNotContainsString('895e092292d88717adaa.woff2', $cssContent, 'custom.css should not contain webpack-generated font references');
    }

    /**
     * Test that theme.css does not contain broken Manrope font references
     */
    public function testThemeCssDoesNotContainBrokenFontReferences(): void
    {
        $themeCssPath = self::THEME_PATH . '/assets/css/theme.css';
        $this->assertFileExists($themeCssPath, 'theme.css file should exist');

        $cssContent = file_get_contents($themeCssPath);
        $this->assertNotEmpty($cssContent, 'theme.css should not be empty');

        // Verify no references to broken webpack-generated font files
        $brokenFontPatterns = [
            '895e092292d88717adaa.woff2',
            '83131b9daba3e9a7b2c7.woff',
            '057cc3c927dc0b2e8dbb.otf',
        ];

        foreach ($brokenFontPatterns as $pattern) {
            $this->assertStringNotContainsString(
                $pattern,
                $cssContent,
                "theme.css should not contain broken font reference: {$pattern}"
            );
        }
    }

    /**
     * Test that theme.css uses system fonts as fallback
     */
    public function testThemeCssUsesSystemFonts(): void
    {
        $themeCssPath = self::THEME_PATH . '/assets/css/theme.css';
        $cssContent = file_get_contents($themeCssPath);

        // Should contain system font stack
        $systemFonts = [
            '-apple-system',
            'BlinkMacSystemFont',
            'Segoe UI',
            'Roboto',
        ];

        $hasSystemFonts = false;
        foreach ($systemFonts as $font) {
            if (stripos($cssContent, $font) !== false) {
                $hasSystemFonts = true;
                break;
            }
        }

        $this->assertTrue($hasSystemFonts, 'theme.css should include system fonts as fallback');
    }

    /**
     * Test that required theme assets directories exist
     */
    public function testRequiredDirectoriesExist(): void
    {
        $requiredDirs = [
            'assets',
            'assets/css',
            'assets/js',
            'config',
            'templates',
        ];

        foreach ($requiredDirs as $dir) {
            $dirPath = self::THEME_PATH . '/' . $dir;
            $this->assertDirectoryExists($dirPath, "Required directory '{$dir}' should exist");
        }
    }

    /**
     * Test that theme documentation files exist
     */
    public function testDocumentationFilesExist(): void
    {
        $docFiles = [
            'README.md',
            'TROUBLESHOOTING.md',
        ];

        foreach ($docFiles as $file) {
            $filePath = self::THEME_PATH . '/' . $file;
            $this->assertFileExists($filePath, "Documentation file '{$file}' should exist");
        }
    }

    /**
     * Test that custom CSS contains brand color variables
     */
    public function testCustomCssContainsBrandColors(): void
    {
        $customCssPath = self::THEME_PATH . '/assets/css/custom.css';
        $cssContent = file_get_contents($customCssPath);

        // Check for brand color CSS variables
        $brandColors = [
            '--logo-brown',
            '--logo-orange',
            '--logo-red',
            '--dark-brown',
            '--soft-tan',
        ];

        foreach ($brandColors as $colorVar) {
            $this->assertStringContainsString(
                $colorVar,
                $cssContent,
                "custom.css should contain brand color variable: {$colorVar}"
            );
        }
    }

    /**
     * Test that theme version is correct
     */
    public function testThemeVersionIsCorrect(): void
    {
        $configPath = self::THEME_PATH . '/config/theme.yml';
        $parser = new Parser();
        $config = $parser->parseFile($configPath);

        $this->assertArrayHasKey('version', $config);
        $this->assertEquals('0.2.0', $config['version'], 'Theme version should be 0.2.0');
    }
}
