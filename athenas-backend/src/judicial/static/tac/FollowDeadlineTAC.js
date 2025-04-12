Ext._define('judicial.tac.FollowDeadlineTAC', {

    extend: 'Ext.Panel',

    getManagementTacGrid: function(cfg) {
        if(!this._managementTacGrid){
            this._managementTacGrid = Ext._create('judicial.tac.ManagementTACGrid', {
                title: 'Termos de ajustes de conduta',
                region: 'center',
                minWidth: 500,
                allowUpdate: false,
                allowRemove: false,
                columnAction: false,
                gridAutoLoad: (cfg.gridAutoLoad !== undefined ? cfg.gridAutoLoad : true),
                hideItemsToolbar: ['add', 'edit','remove', 'download'],
            });

            this._managementTacGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();

                    if(selection.length > 0)
                        this.managementTac(selection[0].get('pk'));
                    else
                        this.managementTac(null);
                }
            });
        }


        return this._managementTacGrid;
    },


    getActivityGrid: function(cfg) {
        if(!this._activityGrid) {
            this._activityGrid = Ext._create('judicial.tac.ActivityGrid', {
                title: 'Cláusulas a serem cumpridas',
                region: 'center',
                minWidth: 575,
                width: 575,
                enabled: false,
                // allowUpdate: false,
                allowRemove: false,
                columnAction: false,
                gridAutoLoad: false,
                disabled: true,
                hideItemsToolbar: ['add', 'edit','remove', 'download'],
            });

            this._activityGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();

                    if(selection.length > 0)
                        this.activity(selection[0].get('pk'));
                    else
                        this.activity(null);
                }
            });

        }

        return this._activityGrid;
    },

    activity: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._activity = value;

            if(dispatch) this.observerActivity();
        }

        return this._activity;
    },

    observerActivity: function() {
        var value = this.activity();

        if(value) {
            this.getResponsibleGrid().enable();
            this.getResponsibleGrid().setFilterProperty('activity__pk', value, 100);
        }
        else {
            this.getResponsibleGrid().disable();
            this.getResponsibleGrid().setFilterProperty('activity__pk', 0, 100, false);
            this.getResponsibleGrid().getStore().removeAll();
        }
    },

    getResponsibleGrid: function() {
        if(!this._responsibleGrid) {
            this._responsibleGrid = Ext._create('judicial.tac.ResponsibleGrid', {
                title: 'Executores da cláusula',
                region: 'south',
                split: true,
                minHeight: 400,
                height: 400,
                allowUpdate: false,
                allowRemove: false,
                columnAction: false,
                gridAutoLoad: false,
                disabled: true,
                hideItemsToolbar: ['add','edit', 'remove', 'download'],
            });
        }

        return this._responsibleGrid;
    },

    managementTac: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._managementTac = value;

            if(dispatch) this.observerManagementTac();
        }

        return this._managementTac;
    },

    observerManagementTac: function() {
        var value = this.managementTac();

        if(value) {
            this.getActivityGrid().enable();
            this.getActivityGrid().setFilterProperty('tac__pk', value, 100);
        }
        else {
            this.getActivityGrid().disable();
            this.getActivityGrid().setFilterProperty('tac__pk', 0, 100, false);
            this.getActivityGrid().getStore().removeAll();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Termos de ajuste de atividade'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getManagementTacGrid(cfg),
                    {
                        xtype: 'panel',
                        region: 'east',
                        layout: 'border',
                        border: false,
                        minWidth: 575,
                        width: 750,
                        split: true,
                        items: [
                            this.getActivityGrid(cfg),
                            this.getResponsibleGrid(cfg)
                        ]
                    }
                ]
            }
        );

        judicial.tac.FollowDeadlineTAC.superclass.constructor.call(this, cfg);
    }

});
