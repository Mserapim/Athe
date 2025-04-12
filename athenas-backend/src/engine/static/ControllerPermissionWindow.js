/**
 *
 **/
Ext._define('engine.ControllerPermissionWindow', {
    extend: 'core.RestfulWindow',

    rest: 'engine.ControllerPermissionRestful',

    width: 575,

    getTabPanel: function(cfg) {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                height: 535,
                border: false,
                items: [
                    this.getMainPanel(cfg)
                ]
            });

        return this._tabPanel;
    },

    getMainPanel: function(cfg) {
        if (cfg && cfg.ownerGrid && cfg.ownerGrid.autoPermissionsFuncs) {
            var autoFunc = cfg.ownerGrid.autoPermissionsFuncs
        }

        var name_field = {
            fieldLabel: 'Slug',
            xtype: 'textfield',
            name: 'name',
            maxLenght: 100,
            allowBlank: false,
            width: 300
        };
        var is_default_field = {
            boxLabel: 'Permissões de funcionalidade padrão',
            xtype: 'checkbox',
            name: 'is_default',
        };
        var manager_permission_field = {
            boxLabel: 'Permissões de funcionalidade gestor',
            xtype: 'checkbox',
            name: 'manager_permission',
        };
        var controllers_field = {
            xtype: 'rest-relatedfield',
            fieldLabel: 'Funcionalidades',
            name: 'controllers',
            relatedname: 'controller_permissions',
            width: 445,
            height: 180,
            rest: this.rest,
            sourceRest: 'engine.ControllerRestful',
            oId: cfg.oId
        };
        var users_field = {
            xtype: 'rest-relatedfield',
            fieldLabel: 'Usuários',
            name: 'users',
            relatedname: 'controller_permissions',
            width: 445,
            height: 180,
            rest: this.rest,
            sourceRest: 'auth.UserRestful',
            oId: cfg.oId
        };

        var items = [];

        items.push(name_field);
        
        if (autoFunc == 'True') {
            items.push(is_default_field);
        }
        
        items.push(manager_permission_field)
        items.push(controllers_field);
        items.push(users_field);
        
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                layout: 'form',
                border: false,
                frame: true,
                title: 'Principal',
                items: items
            });

        return this._mainPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                items: [
                    this.getTabPanel(cfg)
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.getFormPanel().getForm().findField('controllers').objectId(instance.pk);
                    this.getFormPanel().getForm().findField('users').objectId(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        engine.ControllerPermissionWindow.superclass.constructor.call(this, cfg);
    }
});