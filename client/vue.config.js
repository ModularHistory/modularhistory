const BundleTracker = require("webpack-bundle-tracker");

const pages = {
    'vue_app_01': {
        entry: './src/main.js',
        chunks: ['chunk-vendors']
    },
    'vue_app_02': {
        entry: './src/newhampshir.js',
        chunks: ['chunk-vendors']
    },
}

module.exports = {
    pages: pages,
    filenameHashing: false,
    productionSourceMap: false,
    publicPath: process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8080/',
    outputDir: '../django_vue_mpa/static/vue/',
    // outputDir: '../server/static/dist',
    // indexPath: '../../templates/base-vue.html', // relative to outputDir!

    chainWebpack: config => {
        config.optimization
            .splitChunks({
                cacheGroups: {
                    vendor: {
                        test: /[\\/]node_modules[\\/]/,
                        name: "chunk-vendors",
                        chunks: "all",
                        priority: 1
                    },
                },
            });
        Object.keys(pages).forEach(page => {
            config.plugins.delete(`html-${page}`);
            config.plugins.delete(`preload-${page}`);
            config.plugins.delete(`prefetch-${page}`);
        })
        config
            .plugin('BundleTracker')
            .use(BundleTracker, [{filename: '../client/webpack-stats.json'}]);
        config.resolve.alias
            .set('__STATIC__', 'static')
        config.devServer
            .public('http://localhost:8080')
            .host('localhost')
            .port(8080)
            .hotOnly(true)
            .watchOptions({poll: 1000})
            .https(false)
            .headers({"Access-Control-Allow-Origin": ["*"]})
    }

    // chainWebpack: config => {
    //     /*
    //     The arrow function in writeToDisk(...) tells the dev server to write
    //     only index.html to the disk.
    //
    //     The indexPath option (see above) instructs Webpack to also rename
    //     index.html to base-vue.html and save it to Django templates folder.
    //
    //     We don't need other assets on the disk (CSS, JS...) - the dev server
    //     can serve them from memory.
    //
    //     See also:
    //     https://cli.vuejs.org/config/#indexpath
    //     https://webpack.js.org/configuration/dev-server/#devserverwritetodisk-
    //     */
    //     config.devServer
    //         .public('http://127.0.0.1:8080')
    //         .hotOnly(true)
    //         .headers({"Access-Control-Allow-Origin": "*"})
    //         .writeToDisk(filePath => filePath.endsWith('index.html'));
    // }
}
