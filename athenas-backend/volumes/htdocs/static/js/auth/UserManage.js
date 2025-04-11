/**
 *
 **/
Ext._define('auth.UserManage', {
    extend: 'toolkit.widget.TabPanel',

    getUserGrid: function() {
        if(!this._userGrid) {
            this._userGrid = Ext._create('auth.UserGrid', {
                flex: 1
            });

            this._userGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selected = sm.getSelected();

                    if(selected)
                        this.user(selected.get('pk'));
                    else
                        this.user(null);
                }
            });
            this._userGrid.getStore().on({
                scope: this,
                load: function() {
                    var selected = (this._userGrid.getSelectionModel().getSelected());

                    if(selected){
                      this.getGroupPermissionField().getGridPanel().getStore().load();
                      this.getControllerPermissionField().getGridPanel().getStore().load();
                     }
                }
            });
        }

        return this._userGrid;
    },

    getGroupPermissionField: function() {
        if(!this._groupPermissionField)
            this._groupPermissionField = Ext._create('core.fields.RelatedRestfulField', {
                flex: 1,
                title: 'Grupo de Permissões',
                rest: 'auth.UserRestful',
                sourceRest: 'auth.GroupRestful',
                name: 'groups',
                relatedname: 'users',
                border: false,
                width: 550
            });

        return this._groupPermissionField;
    },

    getControllerPermissionField: function() {
        if(!this._controllerPermissionField)
            this._controllerPermissionField = Ext._create('core.fields.RelatedRestfulField', {
                flex: 1,
                title: 'Grupo de Funcionalidades',
                style: {marginTop: '4px'},
                rest: 'auth.UserRestful',
                sourceRest: 'engine.ControllerPermissionRestful',
                name: 'controllerpermission_set',
                relatedname: 'users',
                border: false,
                width: 550
            });

        return this._controllerPermissionField;
    },

    getDetailPanel: function() {
        if(!this._detailPanel)
            this._detailPanel = Ext._create('Ext.Container', {
                width: 550,
                layout: {
                    type: 'vbox',
                    align: 'stretch'
                },
                style: {
                    paddingLeft: '4px'
                },
                items: [
                    this.getGroupPermissionField(),
                    this.getControllerPermissionField()
                ]
            });

        return this._detailPanel;
    },

    user: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._user = value;

            if(!prevent) this.observeUser();
        }

        return this._user;
    },

    observeUser: function() {
        var value = this.user();

        if(value) {
            this.getGroupPermissionField().objectId(value);
            this.getControllerPermissionField().objectId(value);
        }
        else {
            this.getGroupPermissionField().objectId(null);
            this.getControllerPermissionField().objectId(null);
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Usuário'
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                items: [
                    this.getUserGrid(),
                    this.getDetailPanel()
                ]
            }
        );

        // this.callParent([cfg]);
        auth.UserManage.superclass.constructor.call(this, cfg);
        this.observeUser();
    }
});
