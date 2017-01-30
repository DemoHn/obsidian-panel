/* global env:true rm:true mkdir:true cp:true */
// https://github.com/shelljs/shelljs
require('./check-versions')()
require('shelljs/global')
env.NODE_ENV = 'production'

var path = require('path')
var config = require('../config')
var ora = require('ora')
var webpack = require('webpack')
var webpackConfig = require('./webpack.prod.conf')
var fs = require("fs")
console.log(
  '  Tip:\n' +
  '  Built files are meant to be served over an HTTP server.\n' +
  '  Opening index.html over file:// won\'t work.\n'
)

var spinner = ora('building for production...')
spinner.start()

var assetsPath = path.join(config.build.assetsRoot, config.build.assetsSubDirectory);
//rm("-R", assetsPath)
cp('-R','server_inst.index.html',assetsPath+"/../templates/server_inst/index.html");
cp('-R','super_admin.index.html',assetsPath+"/../templates/superadmin/index.html");
cp('-R','startup.index.html',assetsPath+"/../templates/startup/index.html");
webpack(webpackConfig, function (err, stats) {
    fs.writeFileSync("stats.json", JSON.stringify(stats.toJson("verbose")));
    /*console.log(stats.toString({
        modules: true,
        reasons: false,
        colors: true,
        modulesSort : "size"
    }));*/
  spinner.stop()
  if (err) throw err
  process.stdout.write(stats.toString({
    colors: true,
    modules: false,
    children: false,
    chunks: false,
    chunkModules: false
  }) + '\n')
})
