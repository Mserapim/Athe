Ext._define('planning.hiring.minute.MinuteManage', {
    extend: 'toolkit.widget.TabPanel',

    getMinuteGrid: function() {
        if(!this._minuteGrid) {
            this._minuteGrid = Ext._create('planning.hiring.minute.MinuteGrid', {
                region: 'center',
                columnAction: false,
                baseParams: {
                    filter: Ext.encode([{
                        property: 'status__in',
                        value: [1],
                        stage: 1000
                    }])
                }
            });

            this._minuteGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    var selection = selm.getSelections();
                    if (selection.length > 0) {
                        this.minute(selection[0].id);
                    } else {
                        this.minute(null);
                    }
                }
            });

            this._minuteGrid.getStore().on({
                scope:this,
                load: function() {
                    this.observeMinute();
                }
            });
        }

        return this._minuteGrid;
    },

    getHistoryGrid: function() {
        if (!this._historyGrid)
            this._historyGrid = Ext._create('planning.hiring.minuteaction.MinuteActionGrid', {
                title: 'Histórico',
                gridAutoLoad: false,
            });

        return this._historyGrid;
    },

    getTabs: function() {
        if (!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                region: 'south',
                split: true,
                activeTab: 0,
                scope: this,
                height: 200,
                items: [
                    this.getHistoryGrid(),
                ]
            });

        return this._tabPanel;
    },

    getFeedbackDisplayTilePanel: function() {
        if (!this._feedbackDisplayTilePanel)
            this._feedbackDisplayTilePanel = Ext._create('core.TilePagePanel', {
                title: 'Resumo',
                region: 'east',
                height: '100%',
                width: '40%',
                split: true
            });

        return this._feedbackDisplayTilePanel;
    },

    minute: function(value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined){
            this._minute = value;

            if (observe)
                this.observeMinute();
        }
        return this._minute;
    },

    observeMinute: function() {
        var value = this.minute();
        tilePanel = this.getFeedbackDisplayTilePanel();

        if (value) {
            this.getHistoryGrid().enable();
            this.getHistoryGrid().setParam('minute', value);
            this.getHistoryGrid().setFilterProperty('minute', value, 10);

            // Início do trecho referente ao tile
            var rest = this.getMinuteGrid().factoryRestful();
            var mask = new Ext.LoadMask(tilePanel.getEl(), { msg: 'buscando documento...'});
            mask.show();
            rest.rendererDocument(
                value, {
                    scope: this,
                    fn: function(document) {
                        tilePanel.enable();
                        tilePanel.setPageContent(document.content);
                    }
                }, {
                    fn: function(message) {
                        Ext.Msg.show({
                            title: 'Buscando documento',
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                }, {
                    fn: function() {
                        mask.hide();
                    }
                }
            );
        } else {
            this.getHistoryGrid().disable();
            this.getHistoryGrid().setParam('minute', 0);
            this.getHistoryGrid().setFilterProperty('minute', 0, 10);

            tilePanel.setPageContent('');
            tilePanel.disable();
        }
    },

    getGrouping: function() {
        if (!this._grouping)
            this._grouping = Ext._create('Ext.Panel', {
                region: 'center',
                layout: 'border',
                split: true,
                items: [
                    this.getMinuteGrid(),
                    this.getTabs()
                ],
            });

        return this._grouping;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Atas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGrouping(),
                    this.getFeedbackDisplayTilePanel(cfg),
                ]
            }
        );

        planning.hiring.minute.MinuteManage.superclass.constructor.call(this, cfg);
        this.observeMinute();
    }
});

