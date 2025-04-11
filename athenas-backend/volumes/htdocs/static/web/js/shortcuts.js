var vroot = '/'+CONTEXT+'/';
var mroot = vroot+'static/';
var icons = mroot+'/web/icons/';
var xt = Ext;
var xMsg = xt.Msg;
var xPanel = xt.Panel;
var xWindow = xt.Window;
var xPanel = xt.Panel;
var xGrid = xt.grid.GridPanel;
var xDataView = xt.DataView;
var xColumn = xt.grid.ColumnModel;
var xSelection = xt.grid.RowSelectionModel;
var xJsonStore = xt.data.JsonStore;
var xPaging = xt.PagingToolbar;
var xTree = xt.tree.TreePanel;
var xForm = xt.FormPanel;
var xCombo = xt.form.ComboBox;
var xAjax = xt.Ajax;
var xTemplate = xt.XTemplate;

var action = function(ctrl, act, args)
{
    if (ctrl.indexOf('/') != -1)
    {
        args = ctrl.split('/');
        ctrl = args.splice(0, 1);
        act = args.splice(0, 1);
    }
    return toolkit.util.Normalize.controller_action(ctrl, act, args);
}

var xMessage = function(opts)
{
    var defaults = {
        title:'Aviso',
        width: 350,
        msg:'',
        buttons:{ok:'Ok'},
        icon:xMsg.INFO,
        fn:null,
        animEl:null
    };
    var config = xt.apply(defaults, opts);
    xMsg.show(config);
}

var xAlert = function(opts)
{
    if(xt.isString(opts)) opts = {msg:opts};
    xMessage(opts);
}

var xConfirm = function(opts)
{
    var config = {};
    var defaults = {
        title:'Atenção',
        msg:'',
        buttons:{ok:'Sim', no:'Não'},
        icon:xMsg.QUESTION,
        fn:null,
        animEl:null
    };

    var config = xt.apply(defaults, opts);
    xMessage(config);
}

var xPrompt = function(opts)
{
    var defaults = {
        title:'Prompt',
        msg:'',
        fn:null
    };
    var config = xt.apply(defaults, opts);
    xMsg.prompt(config.title, config.msg, config.fn);
}


