
Ext._define('raf.FillAdjustmentManageWindow', {
    extend: 'Ext.Window',

    getInboxPanel: function(cfg) {
        if(!this._inboxPanel) {
            this._inboxPanel = Ext._create('raf.adjustment.AdjustmentEmployeeGrid', {
                region: 'center',
                detailView: this.getTilePanel(cfg),
                params: cfg.values || {},
                columnAction: false,
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
            });

            this._inboxPanel.on(
                'updatedItemGrid',
                function(instance) {
                    if(instance !== undefined)
                        if(instance.activity !== undefined)
                            this.activity(instance.activity);


                    core.invokeCallback((this.callback || {}).success);
                },
                this
            );
            this._inboxPanel.on(
                'createdItemGrid',
                function(instance) {
                    if(instance !== undefined)
                        if(instance.activity !== undefined)
                            this.activity(instance.activity);

                    core.invokeCallback((this.callback || {}).success);
                },
                this
            );
        }

        return this._inboxPanel;
    },

    activity: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._activity = value;

            if(dispatch) this.observeActivity();
        }

        return this._activity;
    },

    observeActivity: function() {
        var value = this.activity();

        if(value) {
            this.getInboxPanel().setFilterProperty('activity', value, 1000);
        }
        else {
            this.getInboxPanel().setFilterProperty('activity', 0, 1000, false);
            this.getInboxPanel().getStore().removeAll();
        }
    },

    getTilePanel: function(cfg) {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                region: 'east',
                split: true,
                width: (Ext.getBody().getBox().width * 0.8) * 0.6,
                // minWidth: cfg.getWidth() * 0.5,
                // width: 850,
                // minWidth: 850
            });

        return this._tilePanel;
    },


    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ];

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Ajuste de atividade',
                modal: true,
                width: Ext.getBody().getBox().width * 0.8,
                height: Ext.getBody().getBox().height * 0.9
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                buttons: this.getButtons(),
                items: [
                    this.getInboxPanel(cfg),
                    this.getTilePanel(cfg)
                ]
            }
        );

        raf.FillAdjustmentManageWindow.superclass.constructor.call(this, cfg);
        this.activity(this.values.activity);
    }
});
