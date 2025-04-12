var getSiteManager = function(show, permissions)
{
    toolkit.web.cms.siteManager = new toolkit.web.cms.Sites(permissions);
    if(show) toolkit.web.cms.siteManager.show();
    return toolkit.web.cms.siteManager;
}

var getAreaManager = function(site, kind, permissions, title, show)
{
    toolkit.web.cms.areaManager = new toolkit.web.cms.Areas(site, kind, permissions, title);
    if(show) toolkit.web.cms.areaManager.show();
    return toolkit.web.cms.areaManager;
}

var getPostManager = function(site, kind, area, area_title, permissions, title, show)
{
    toolkit.web.cms.postManager = new toolkit.web.cms.Posts(site, kind, area, area_title, permissions, 'Posts em '+title);
    if(show) toolkit.web.cms.postManager.show();
    return toolkit.web.cms.postManager;
}

var getLinkManager = function(site, kind, area, area_title, permissions, title, show)
{
    toolkit.web.cms.linkManager = new toolkit.web.cms.links.Manager(site, kind, area, area_title, permissions, 'Links em '+title);
    if(show) toolkit.web.cms.linkManager.show();
    return toolkit.web.cms.linkManager;
}

var getPGJActionsManager = function(site, kind, area, area_title, permissions, title, show)
{
    toolkit.web.cms.pgjActionsManager = new toolkit.web.cms.pgjActions(site, kind, area, area_title, permissions, 'Atuações em '+title);
    if(show) toolkit.web.cms.pgjActionsManager.show();
    return toolkit.web.cms.pgjActionsManager;
}

var getPGJActionStatusesManager = function(show)
{
    toolkit.web.cms.pgjActionStatusesManager = new toolkit.web.cms.pgjActionsStatus();
    if(show) toolkit.web.cms.pgjActionStatusesManager.show();
    return toolkit.web.cms.pgjActionStatusesManager;
}

var getPollManager = function(site, permissions, title, show)
{
    toolkit.web.cms.pollManager = new toolkit.web.cms.Polls(site, permissions, title);
    if(show) toolkit.web.cms.pollManager.show();
    return toolkit.web.cms.pollManager;
}

var getAttachmentsManager = function(post, post_title, show)
{
    toolkit.web.cms.attachmentManager = new toolkit.web.cms.Attachments(post, post_title);
    if(show) toolkit.web.cms.attachmentManager.show();
    return toolkit.web.cms.attachmentManager;
}

var getPermissionsManager = function(area, permissions, show)
{
    toolkit.web.cms.permissionManager = new toolkit.web.cms.Permissions(area, permissions);
    if(show) toolkit.web.cms.permissionManager.show();
    return toolkit.web.cms.permissionManager;
}

var getFieldByName = function(form, name)
{
    var out = '';
    Ext.each(form.items.items, function(item){
        if(item.name == name || item.hiddenName == name)
        {
            out = item;
            return false;
        }
    });
    return out;
}

var showErrors = function(json, form)
{
    Ext.each( json.errors, function(item)
        {
            var field = form.findField(item.name);
            if(field)
                field.markInvalid(item.msgs[0]);
        }
    );
}

var showErrorMessage = function(json, form)
{
    var err = [];
    Ext.each(json.errors, function(item)
        {
            var field = form.findField(item.name);
            if(field)
            {
                var label = field.fieldLabel
                if (!label)
                    label = field.ownerCt.fieldLabel

                var msg = '<strong>' + label + '</strong>: ' + item.msgs[0].toLowerCase();
                err[err.length] = {tag: 'li', html: msg};
            }
        }
    );

    xMessage({
        title: 'Falha',
        msg: Ext.DomHelper.markup({
            tag: 'div', cls: 'error-box',
            children: [
                {tag: 'p', html: json.msg},
                {tag: 'ul', children: err}
            ]
        })
    });
}

var deleteItem = function(opts)
{
    if(opts.signal == 'ok')
    {
        var loading = new Ext.LoadMask(xt.getBody(), {msg: 'Por favor aguarde...', store: opts.store});
        loading.show();
        xAjax.request({
            url: action('CMS/delete/json'),
            params: {id: opts.pars, model: opts.model, rel_id: opts.rel_id},
            success: function(response, options)
            {
                loading.hide();
                json = Ext.decode(response.responseText);
                if(!json.success)
                    xAlert(json.msg);
                else
                {
                    if(opts.success)
                        opts.success();
                    if(opts.store)
                        opts.store.reload();
                }
            }
        });
    }
}


var makePublicationForm = function(opts)
{
    var start = opts.record.get('publication_start');
    if(start)
        start = start.split(' ')[0];

    var end = opts.record.get('publication_end');
    if(end)
        end = end.split(' ')[0];

    var published_date = opts.record.get('published_date');
    if(published_date)
        published_date = published_date.split(' ')[0];

    var pubForm = new ExtFormHelper({
        url: action('CMS/create_publication/json'),
        store: opts.store,
        windowConfig: {
            title: opts.title
        },
        formConfig: {
            labelAlign: 'left',
            labelWidth: 70,
            autoHeight: true,
            autoWidth: true,
            items: [
                {
                    // id: 'content',
                    name: 'content',
                    value: opts.record.get('content'),
                    xtype: 'hidden'
                },
                {
                    // id: 'published',
                    name: 'published',
                    fieldLabel: 'Estatica',
                    value: opts.record.get('published'),
                    checked: opts.record.get('published'),
                    xtype: 'checkbox',
                    listeners: {
                        check: function(checkbox, checked)
                        {
                            if(checked)
                            {
                                pubForm.find('name', 'publication_start')[0].disable();
                                pubForm.find('name', 'publication_end')[0].disable();
                                pubForm.find('name', 'published_date')[0].enable();
                            }
                            else
                            {
                                pubForm.find('name', 'publication_start')[0].enable();
                                pubForm.find('name', 'publication_end')[0].enable();
                                pubForm.find('name', 'published_date')[0].disable();
                            }
                        }
                    }
                },
                {
                    // id: 'published_date',
                    name: 'published_date',
                    value: published_date,
                    format: 'd/m/Y',
                    xtype: 'datefield'
                },
                {
                    xtype: 'fieldset',
                    autoHeight: true,
                    title: 'Dinâmica',
                    width: 210,
                    items: [
                        {
                            // id: 'publication_start',
                            name: 'publication_start',
                            fieldLabel: 'Data inicio',
                            value: start,
                            format: 'd/m/Y',
                            xtype: 'datefield'
                        },
                        {
                            // id: 'publication_end',
                            name: 'publication_end',
                            fieldLabel: 'Data fim',
                            value: end,
                            format: 'd/m/Y',
                            xtype: 'datefield'
                        }
                    ]
                }
            ]
        }
    });

    pubForm.on(
        'render',
        function()
        {
            pubForm.find('name', 'published')[0].fireEvent(
                'check',
                pubForm.find('name', 'published')[0],
                opts.record.get('published')
            );
        }
    );

    if(opts.cascade)
    {
        var cmp = pubForm.getFormCmp().add({
            name: 'cascade',
            fieldLabel: 'Aplicar em cascata?',
            xtype: 'checkbox'
        });
    }

    pubForm.show();

    return pubForm;
}

var formMaker = function(opts)
{
    var loading = new xt.LoadMask(xt.getBody(), {msg:'Por favor aguarde...'});
    loading.show();
    var config = {};
    var defaults = {
        modal:true,
        title:'Título do form',
        labelWidth:125,
        fileUpload: false,
        labelAlign:'top',
        buttonText:'Ok',
        autoDestroy:true,
        url:null,
        width:null,
        height:null,
        autoScroll:true,
        items:null,
        store:null,
        success:null,
        failure:null
    };
    config = xt.apply(defaults, opts);

    var windowForm = null;
    var form = new xForm({
        labelAlign:config.labelAlign, labelWidth:config.labelWidth, autoScroll: config.autoScroll,
        frame:true, region:'center', items:config.items, fileUpload: config.fileUpload,
        buttons:[
            {
                text:config.buttonText,
                handler:function(btn, event)
                {
                    form.getForm().submit({
                        url:config.url,
                        waitMsg:'Aguarde...',
                        success: function(form, action)
                        {
                            if(config.store) config.store.reload();
                            if(config.success) config.success(form, action);
                            if(config.autoDestroy) windowForm.destroy();
                        },
                        failure: function(form, action)
                        {
                            json = action.result;
                            switch (action.failureType)
                            {
                                case xt.form.Action.CLIENT_INVALID:
                                    xAlert({title:'Falha', msg:'Os dados do formulário não são válidos'});
                                    break;
                                case xt.form.Action.CONNECT_FAILURE:
                                    xAlert({title:'Falha', msg:'A requisição ajax falhou'});
                                    break;
                                case xt.form.Action.SERVER_INVALID:
                                    showErrorMessage(json, form);
                                    //xAlert({title:'Falha', msg:action.result.msg});
                                    break;
                           }
                           if(config.failure) config.failure(form, action);
                        }
                    });
                }
            }
        ],
        listeners:{
            show:function()
            { loading.hide(); }
        }
    });

    if(config.modal)
    {
        windowForm = new xWindow({
            title: config.title, closable: true, modal:true, layout:'fit', border:false,
            height: config.height, width: config.width, defaults:{margins:'10 10 10 10'}, items:[form],
            listeners:{
                show:function()
                { loading.hide(); }
            }
        });
        return windowForm;
    }
    return form;
}

var ExtFormMaker = formMaker;

var ExtFormHelper = function(opts)
{
    var defaults = {
        buttonText: 'Ok',
        autoDestroy: true,
        refEl: null,
        url: null,
        timeout: 30,
        store: null,
        success: null,
        failure: null,
        formConfig: {},
        windowConfig: {}
    };
    var opts = opts || {};
    var config = Ext.apply(defaults, opts);

    var loading = new Ext.LoadMask(config.refEl || Ext.getBody(), {msg:'Por favor aguarde...'});
    loading.show();

    var formDefaults = {
        oid: 'form-helper-form-cmp',
        labelWidth: 125,
        labelAlign: 'top',
        bodyStyle: 'padding: 10px;',
        listeners: {
            show: function()
            { loading.hide(); }
        },
        getFormCmp: function()
        { return this; }
    }
    var formConfig = Ext.apply(formDefaults, config.formConfig);
    var form = new Ext.form.FormPanel(formConfig);
    var windowForm = null;
    form.addButton({
        text: config.buttonText,
        handler: function(btn, event)
        {
            form.getForm().submit({
                url: config.url,
                waitMsg: 'Aguarde...',
                timeout: config.timeout,
                success: function(form, action)
                {
                    if(config.store) config.store.reload();
                    if(config.success) config.success(form, action);
                    if(config.autoDestroy && windowForm) windowForm.destroy();
                },
                failure: function(form, action)
                {
                    json = action.result;
                    switch (action.failureType)
                    {
                        case Ext.form.Action.CLIENT_INVALID:
                            xAlert({title:'Falha', msg:'Os dados do formulário não são válidos'});
                            break;
                        case Ext.form.Action.CONNECT_FAILURE:
                            xAlert({title:'Falha', msg:'A requisição ajax falhou'});
                            break;
                        case Ext.form.Action.SERVER_INVALID:
                            showErrorMessage(json, form);
                            break;
                   }
                   if(config.failure) config.failure(form, action);
                }
            });
        }
    });

    if(config.windowConfig)
    {
        var windowDefaults = {
            title: 'Título do form',
            closable: true,
            modal: true,
            layout: 'fit',
            border: false,
            items: [form],
            listeners: {
                show: function()
                { loading.hide(); }
            },
            getFormCmp: function()
            { return form; }

        }
        var windowConfig = Ext.apply(windowDefaults, config.windowConfig);
        windowForm = new Ext.Window(windowConfig);
        return windowForm;
    }
    return form;
}
