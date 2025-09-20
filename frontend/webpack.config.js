const path = require('path');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = {
  entry: { main: './src/index.js' },
  output: {
    filename: '[name].bundle.js',
    path: path.resolve(__dirname, 'public/dist'),
    clean: true,
  },
  module: {
    rules: [
      { test: /\.css$/i, use: ['style-loader', 'css-loader'] },
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: 'asset/resource',
        generator: { filename: 'assets/[hash][ext][query]' },
      },
    ],
  },
  resolve: { extensions: ['.js', '.json'] },
  plugins: [
    new CopyPlugin({
      patterns: [
        { from: 'public/*.html', to: '[name].[ext]' },
        { from: 'public/**/*.css', to: '[name].[ext]' },
        { from: 'public/**/*.js', to: '[name].[ext]' },
      ],
    }),
  ],
};
