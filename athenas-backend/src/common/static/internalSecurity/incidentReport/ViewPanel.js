
Ext._define('common.internalSecurity.incidentReport.ViewPanel', {
    extend: 'Ext.Panel',

    audioPath: '/athenas/static/common/internalSecurity/alarm_ok.wav',

    _selectionChangeEvent: function(selectionModel) {
        var selections = selectionModel.getSelections();

        if (selections.length > 0) {
            this.incident(selections[0]);
        } else {
            this.incident(null);
        }
    },

    _gridResizeEvent: function (grid, adjWidth) {
        grid.getKeywordField().setWidth(adjWidth - 350);
    },

    getGrid: function (cfg) {
        if (!this._grid) {
            this._grid = Ext._create('common.internalSecurity.incidentReport.Grid', {
                region: 'west',
                border: false,
                split: true,
                gridAutoLoad: false,
                active: cfg.active,
                hideColumns: cfg.gidHideColumns,
                viewConfig: {
                    getRowClass: function(data) {
                        var classes = [];
                        if (data.get('received_by') === null) {
                          classes.push('grid-not-received-incident');
                        }

                        return classes.join(' ');
                    }
                }
            });

            this._grid.setFilter(cfg.preFilter || []);

            this._grid.getSelectionModel().on({
                scope: this,
                selectionchange: this._selectionChangeEvent,
            });

            this._grid.getStore().on({
				scope: this,
				load: function(gd, opts){
                    this.incidentObserve();
				},
			});

            this._grid.on({
                scope: this,
                resize: this._gridResizeEvent,
            });
        }

        return this._grid;
    },

    incident: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._incident = value;

            if(dispatch)
                this.incidentObserve();
        }

        return this._incident;
    },

    incidentObserve: function() {
        var value = this.incident();

        this.getTilePagePanel().setPageContent('');

        if(value) {
            var rest = Ext._create('common.internalSecurity.incidentReport.Restful');
            var mask = new Ext.LoadMask(this.getTilePagePanel().getEl(), { msg: 'carregando incidente...' });

            mask.show();
            rest.rendered(
                value.get('pk'),
                {
                    scope: this,
                    fn: function(rst) {
                        if(rst.success)
                            this.getTilePagePanel().setPageContent(rst.rendered);
                        else {
                            this.getTilePagePanel().setPageContent('');
                            Ext.Msg.show({
                                title: 'Carregando documento',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    }
                },
                {
                    scope: this,
                    fn: function() {
                        this.getTilePagePanel().setPageContent('');
                        Ext.Msg.show({
                            title: 'Carregando documento',
                            msg: 'Recurso indisponivel no momento.',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {
                    fn: function() { mask.hide() }
                }
            )
        }
    },

    getTilePagePanel: function(cfg) {
        if (!this._tilePagePanel) {
            this._tilePagePanel = Ext._create('core.TilePagePanel', {
                region: 'center',
            });
        }

        return this._tilePagePanel;
    },

    getAudioPlayer: function() {
        if (!this._audioPlayer) {
            this._audioPlayer = new Audio(audioPath);
        }

        return this._audioPlayer;
    },

    _resizeEvent: function (panel, adjWidth) {
        toolkit.util.updateGridAndTileDimensions({
            target: this.getGrid(),
            containerWidth: adjWidth,
        });
    },

    constructor: function(cfg) {
        cfg = cfg || {};
        this.panel_active = true;

        Ext.applyIf(cfg, {
            layout: 'border',
            items: [
                this.getGrid(cfg),
                this.getTilePagePanel(cfg)
            ],
            listeners: {
                scope: this,
                resize: this._resizeEvent,
            },
        });

        common
          .internalSecurity
          .incidentReport
          .ViewPanel
          .superclass
          .constructor
          .call(this, cfg);

        this.on({
            scope: this,
            render: function() {
                if (this.panel_active) {
                    core.RemoteObserver.on('internal-security-alarm', {
                        scope: this,
                        fn: function(opt){
                            this._grid.getStore().reload();
                            this.ownerCt.ownerCt.setTitle('Gestor de Incidentes (*)');
                            if(opt.alarm_sound)
                                this.getAudioPlayer().play();
                        }
                    });
                }
            },
            destroy: function(){ this.panel_active = false; }
        });
    }
});
