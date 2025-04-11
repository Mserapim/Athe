Ext._define('common.document_access.log.Modal', {
    extend: 'Ext.Window',

    getButtons: function (cfg) {
        if (!this._buttons) {
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];
        }

        return this._buttons;
    },

    getGridPanel: function (cfg) {
        if (!this._gridPanel) {
            var gridConfig = cfg.gridConfig || {};

            Ext.applyIf(gridConfig, {gridAutoLoad: true});
            Ext.apply(gridConfig, {region: 'center'});

            this._gridPanel = Ext._create('common.document_access.log.Grid', gridConfig);

            this._gridPanel.getSelectionModel().on({
                scope: this,
                selectionchange: function (selm) {
                    var selections = selm.getSelections();

                    if (selections.length > 0) {
                        this.log(selections[0].id);
                    } else {
                        this.log(null);
                    }
                }
            });

            this._gridPanel.getStore().on({
                scope: this,
                load: function () {
                    this.observeLog();
                }
            });
        }

        return this._gridPanel;
    },

    getFeedbackDisplayTilePanel: function () {
        if (!this._feedbackDisplayTilePanel)
            this._feedbackDisplayTilePanel = Ext._create('core.TilePagePanel', {
                title: 'Resumo',
                region: 'south',
                height: '300px',
                split: true
            });

        return this._feedbackDisplayTilePanel;
    },

    log: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._log = value;

            if (observe)
                this.observeLog();
        }

        return this._log;
    },

    observeLog: function() {
        var value = this.log();
        var tilePanel = this.getFeedbackDisplayTilePanel();

        if (value) {
            var rest = this.getGridPanel().factoryRestful();
            var mask = new Ext.LoadMask(tilePanel.getEl(), { msg: 'Buscando documento...' });

            mask.show();

            rest.rendererDocument(
                value,
                {
                    scope: this,
                    fn: function (document) {
                        tilePanel.enable();
                        tilePanel.setPageContent(document.content);
                    }
                },
                {
                    fn: function (message) {
                        Ext.Msg.show({
                            title: 'Buscando documento',
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {
                    fn: function () {
                        mask.hide();
                    }
                }
            );
        } else {
            tilePanel.setPageContent('');
            tilePanel.disable();
        }
    },

    _postConstructor: function (cfg) {
        if (cfg.controlId) {
            this.getGridPanel().setFilterProperty('control', cfg.controlId, 1001);
        }
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Logs',
            width: 1100,
            height: 600,
            modal: true,
        });

        Ext.apply(cfg, {
            layout: 'border',
            items: [
                this.getGridPanel(cfg),
                this.getFeedbackDisplayTilePanel(cfg)
            ],
            buttons: this.getButtons(cfg),
        });

        common.document_access.log.Modal.superclass.constructor.call(this, cfg);

        this.observeLog();
        this._postConstructor(cfg);
    }
});
