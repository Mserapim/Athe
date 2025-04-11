Ext._define('common.saci.attendance.HistoricStepWindow', {
    extend: 'Ext.Window',

    width: 900,


    step: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._step = value;

            if(dispatch)
                this.observerStep();
        }

        return this._step;
    },

    observerStep: function() {
        var value = this.step();

        if(value) {
            var rest = Ext._create('common.saci.step.Restful');
            var mask = new Ext.LoadMask(this.getForwardTilePanel().getEl(), {msg: 'buscando documento...'});
            mask.show();
            rest.rendererDocument(
                value,
                {
                    scope: this,
                    fn: function(document) {
                        this.getForwardTilePanel().enable();
                        this.getForwardTilePanel().setPageContent(document.content);
                    }
                },
                {
                    fn: function(message) {
                        Ext.Msg.show({
                            title: 'Buscando documento',
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {fn: function() {mask.hide();}}
            );

        }
        else {
            this.getForwardTilePanel().disable();
            this.getForwardTilePanel().setPageContent('');
        }
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                items: [
                    this.getStepGrid(cfg),
                    this.getForwardTilePanel()
                ]
            });

        return this._formPanel;
    },



    getForwardTilePanel: function() {
        if(!this._feedbackTilePanel)
            this._feedbackTilePanel = Ext._create('core.TilePagePanel', {
                disabled: true,
                height: 300,
                minHeight: 300,
                papperModel: 'card'
            });

        return this._feedbackTilePanel;
    },


    getStepGrid: function(cfg) {
        if(!this._stepGrid) {
            this._stepGrid = Ext._create('common.saci.step.Grid', {
                configOrderToolBar: [],
                scope: this,
                height: 200,
                columnAction: false,
                border: false,
                gridAutoLoad: true,
                doubleClickHandler: function(){},
            });
            this._stepGrid.setFilterProperty('attendance__pk', cfg.attendance, 100);

            this._stepGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
                    if(selection.length > 0)
                        this.step(selection[0].get('pk'));
                    else
                        this.step(null);
                }
            });
        }
        return this._stepGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Histórico de encaminhamento'
        });

        Ext.apply(cfg, {
            width: 900,
            items: [
                this.getFormPanel(cfg)
            ],
            buttons: [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });

        common.saci.attendance.HistoricStepWindow.superclass.constructor.call(this, cfg);
    }
});
