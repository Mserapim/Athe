/**
 *
 **/
Ext._define('rh.profile.JobProfileManage', {
    extend: 'toolkit.widget.TabPanel',

    getJobProfileGrid: function() {
        if(!this._jobProfileGrid) {
            this._jobProfileGrid = Ext._create('rh.profile.JobProfileGrid', {
                gridAutoLoad: false,
                region: 'north',
                minHeight: 300,
                height: 300,
                split: true
            });

            this._jobProfileGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selmodel) {
                    var data = selmodel.getSelected();

                    if(data)
                        this.jobProfile(data.get('pk'));
                    else
                        this.jobProfile(null);
                }
            });
        }

        return this._jobProfileGrid;
    },

    getWorkplaceGrid: function() {
        if(!this._workplaceGrid) {
            this._workplaceGrid = Ext._create('rh.workplace.Grid', {
                region: 'west',
                minWidth: 375,
                width: 375,
                split: true,
                configOrderToolBar: ['search', '->', 'download'],
                doubleClickHandler: function() {},
                keywordFieldWidth: 215,
                onlyColumns: ['unicode', 'ativo'],
                columnAction: false
            });

            this._workplaceGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selmodel) {
                    var data = selmodel.getSelected();

                    if(data)
                        this.workplace(data.get('pk'));
                    else
                        this.workplace(null);
                }
            });
        }

        return this._workplaceGrid;
    },

    workplace: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._workplace = value;

            if(!prevent) this.observeWorkplace();
        }

        return this._workplace;
    },

    observeWorkplace: function() {
        var value = this.workplace();

        if(value) {
            this.getJobProfileGrid().enable();
            this.getJobProfileGrid().setParam('workplace', value);
            this.getJobProfileGrid().setFilterProperty('linked_workplaces', value, 101);
        }
        else {
            this.getJobProfileGrid().disable();
            this.getJobProfileGrid().setParam('workplace', 0);
            this.getJobProfileGrid().setFilterProperty('linked_workplaces', 0, 101, false);
            this.getJobProfileGrid().getStore().removeAll();
        }

        this.jobProfile(null);
    },

    getJobProfileDetailPanel: function() {
        if(!this._jobProfileDetailPanel)
            this._jobProfileDetailPanel = Ext._create('Ext.Panel', {
                region: 'center',
                minHeight: 500,
                border: false,
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                items: [
                    this.getPermissionField(),
                    this.getGroupField(),
                    this.getControllerPermissionField()
                ]
            });

        return this._jobProfileDetailPanel;
    },

    jobProfile: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._jobProfile = value;

            if(!prevent) this.observeJobProfile();
        }

        return this._jobProfile;
    },

    observeJobProfile: function() {
        var value = this.jobProfile();

        this.getPermissionField().objectId(value);
        this.getGroupField().objectId(value);
        this.getControllerPermissionField().objectId(value);
    },

    getPermissionField: function() {
        if(!this._permissionField)
            this._permissionField = Ext._create('core.fields.RelatedRestfulField', {
                flex: 1,
                title: 'Permissões diretas',
                rest: 'rh.profile.JobProfileRestful',
                sourceRest: 'auth.PermissionRestful',
                name: 'permissions',
                relatedname: 'in_job_profiles',
                border: false
            });

        return this._permissionField;
    },

    getGroupField: function() {
        if(!this._groupField)
            this._groupField = Ext._create('core.fields.RelatedRestfulField', {
                flex: 1,
                title: 'Grupo de Permissões',
                rest: 'rh.profile.JobProfileRestful',
                sourceRest: 'auth.GroupRestful',
                name: 'groups',
                relatedname: 'in_job_profiles',
                border: false
            });

        return this._groupField;
    },

    getControllerPermissionField: function() {
        if(!this._controllerPermissionField)
            this._controllerPermissionField = Ext._create('core.fields.RelatedRestfulField', {
                flex: 1,
                title: 'Funcionalidades',
                rest: 'rh.profile.JobProfileRestful',
                sourceRest: 'engine.ControllerPermissionRestful',
                name: 'features',
                relatedname: 'in_job_profiles',
                border: false
            });

        return this._controllerPermissionField;
    },

    getDetailPanel: function() {
        if(!this._detailPanel)
            this._detailPanel = Ext._create('Ext.Panel', {
                region: 'center',
                minWidth: 600,
                layout: 'border',
                border: false,
                items: [
                    this.getJobProfileDetailPanel(),
                    this.getJobProfileGrid()
                ]
            });

        return this._detailPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Perfil de Acesso'
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getDetailPanel(),
                    this.getWorkplaceGrid()
                ]
            }
        );

        // this.callParent([cfg]);
        rh.profile.JobProfileManage.superclass.constructor.call(this, cfg);
        this.observeWorkplace();
    }
});
