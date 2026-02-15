/**
 * Entretelas Theme - Webpack Configuration
 * Based on PrestaShop Hummingbird theme structure
 */

const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = (env, argv) => {
  const mode = argv.mode || 'production';
  const isDev = mode === 'development';

  return {
    mode,
    entry: {
      theme: [
        './js/theme.js',
        './css/theme.scss'
      ]
    },
    output: {
      path: path.resolve(__dirname, '../assets'),
      filename: 'js/[name].js',
      chunkFilename: 'js/[chunkhash]-chunk.js',
    },
    module: {
      rules: [
        // JavaScript/Babel
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env']
            }
          }
        },
        // SCSS/CSS
        {
          test: /\.(scss|css)$/,
          use: [
            MiniCssExtractPlugin.loader,
            'css-loader',
            'postcss-loader',
            'sass-loader'
          ]
        }
      ]
    },
    plugins: [
      new MiniCssExtractPlugin({
        filename: 'css/[name].css'
      })
    ],
    externals: {
      prestashop: 'prestashop',
      $: 'jquery',
      jquery: 'jQuery'
    },
    devtool: isDev ? 'source-map' : false,
    optimization: {
      minimize: !isDev,
      minimizer: [
        new TerserPlugin({
          extractComments: false,
          terserOptions: {
            compress: {
              drop_console: !isDev
            }
          }
        })
      ]
    },
    performance: {
      hints: isDev ? false : 'warning',
      maxAssetSize: 512000,
      maxEntrypointSize: 512000
    }
  };
};
