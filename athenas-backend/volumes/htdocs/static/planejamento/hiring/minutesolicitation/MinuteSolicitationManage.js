Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationManage', {
    extend: 'toolkit.widget.TabPanel',

    getMinuteSolicitationGrid: function() {
        if(!this._minuteSolicitationManagerGrid) {
            this._minuteSolicitationManagerGrid = Ext._create('planning.hiring.minutesolicitation.MinuteSolicitationManagerGrid', {
                region: 'center',
            });

            this._minuteSolicitationManagerGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    var selection = selm.getSelections();
                    if (selection.length > 0) {
                        this.solicitation(selection[0].id);
                    } else {
                        this.solicitation(null);
                    }
                }
            });

            this._minuteSolicitationManagerGrid.getStore().on({
                scope:this,
                load: function() {
                    this.observeSolicitation();
                }
            });
        }

        return this._minuteSolicitationManagerGrid;
    },

    getMinuteSolicitationActionGrid: function() {
        if(!this._minuteSolicitationActionGrid) {
            this._minuteSolicitationActionGrid = Ext._create('planning.hiring.minutesolicitationaction.MinuteSolicitationActionGrid', {
                region: 'south',
                gridAutoLoad: false,
                height: 200,
            });
        }

        return this._minuteSolicitationActionGrid;
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

    solicitation: function(value, observe) {
        observe = (observe === undefined ? true : observe);
        
        if (value !== undefined){
            this._solicitation = value;

            if (observe)
                this.observeSolicitation();
        }
        return this._solicitation;
    },

    observeSolicitation: function() {
        var value = this.solicitation();
        tilePanel = this.getFeedbackDisplayTilePanel();
        
        if (value) {
            this.getMinuteSolicitationActionGrid().enable();
            this.getMinuteSolicitationActionGrid().setParam('solicitation', value);
            this.getMinuteSolicitationActionGrid().setFilterProperty('solicitation', value, 10);
            
            // Início do trecho referente ao tile
            var rest = this.getMinuteSolicitationGrid().factoryRestful();
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
            this.getMinuteSolicitationActionGrid().disable();
            this.getMinuteSolicitationActionGrid().setParam('solicitation', 0);
            this.getMinuteSolicitationActionGrid().setFilterProperty('solicitation', 0, 10);

            tilePanel.setPageContent('');
            tilePanel.disable();

        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Pedidos'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGrouping(),
                    this.getFeedbackDisplayTilePanel()
                ]
            }
        );

        planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerManage.superclass.constructor.call(this, cfg);
        this.observeSolicitation();
    }
});

