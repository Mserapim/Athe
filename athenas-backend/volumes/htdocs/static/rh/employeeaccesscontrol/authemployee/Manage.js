/**
 *
 **/

 Ext._define('rh.employeeaccesscontrol.authemployee.Manage', {
    extend: 'toolkit.widget.TabPanel',
  
    getGrid: function () {
        if (!this._grid) {
            this._grid = Ext._create('rh.employeeaccesscontrol.authemployee.Grid', {
                flex: 1
            });

            this._grid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selected = sm.getSelected();

                    var selected = sm.getSelected();
                    if(selected)
                        this.user(selected.get('user_pk'));
                    else
                        this.user(null);
                }
            });
            this._grid.getStore().on({
                scope: this,
                load: function() {
                    var selected = (this._grid.getSelectionModel().getSelected());

                    if(selected){
                      this.getGroupPermissionField().getGridPanel().getStore().load();
                      this.getControllerPermissionField().getGridPanel().getStore().load();
                     }
                }
            });
        }
  
        return this._grid;
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
  
    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
  
         Ext.applyIf(
            cfg,
            {
            title: 'Gestor de usuários'
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
                    this.getGrid(),
                    this.getDetailPanel()
                ]
            }
        );
  
        rh.employeeaccesscontrol.authemployee.Manage.superclass.constructor.call(this, cfg);
        this.observeUser();
    }
});
  