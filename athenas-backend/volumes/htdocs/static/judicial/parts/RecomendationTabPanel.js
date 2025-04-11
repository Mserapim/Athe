
Ext._define('judicial.parts.RecomendationTabPanel', {
    extend: 'Ext.Panel',
    
    getRecomendationGrid: function(cfg) {
        if (!this._recomendationGrid) {
            var self = this;

            this._recomendationGrid = Ext._create('judicial.parts.RecomendationGrid', {
                title: 'Recomendações',
                region: 'center',
                minWidth: 500,
                allowCreate: false,
                allowRemove: false,
                allowUpdate: false,
            	columnAction: false,
                gridAutoLoad: (cfg.gridAutoLoad !== undefined ? cfg.gridAutoLoad : true),
            	hideItemsToolbar: ['add', 'remove', 'download', 'edit'],
                hiddenColumns: ['']
            });
            
            this._recomendationGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
    
                    if(selection.length > 0)
                        this.recomendation(selection[0].get('pk'));
                    else
                        this.recomendation(null);
                }
            });
        }

        return this._recomendationGrid;
    },

    recomendation: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
    
        if(value !== undefined) {
            this._recomendation = value;
    
            if(dispatch)
                this.recomendationObserve();
        }
    
        return this._recomendation;
    },

    recomendationObserve: function() {
        var recomendation = this.recomendation();
        this.getTilePanel().setPageContent('');
        tile = this.getTilePanel();

        if(recomendation) {
            var rest = Ext._create('judicial.parts.RecomendationRestful');
            var mask = new Ext.LoadMask(tile.getEl(), {msg: 'carregando documento...'});
            
            mask.show();
            rest.rendered(
                recomendation, 
                {
                    scope: this,
                    fn: function(rst) {
                        if(rst.success) {
                            tile.setPageContent(rst.rendered);
                            (rst.extra_pages || []).forEach(
                                function(page) {
                                    tile.addPageContent(page);
                                }
                            );
                        }else {
                            tile.setPageContent('');
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
                        tile.setPageContent('');
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

    getTilePanel: function(cfg) {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                flex: 1,
                papperModel: (cfg.tilePapperModel || 'a4')
            });
    
        return this._tilePanel;
    },

    getDocumentPanel: function(cfg) {
        if(!this._recomendationControlPanel)
            this._recomendationControlPanel = Ext._create('Ext.Panel', {
                region: 'east',
                minWidth: 830,
                width: 830,
                split: true,
                layout: {
                    type: 'vbox',
                    align: 'stretch',
                },
                items: [
                    this.getTilePanel(cfg),
                ]
            });
    
        return this._recomendationControlPanel;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            layout: 'border',
            items:[
                this.getRecomendationGrid(cfg),
                this.getDocumentPanel(cfg)
            ]
        });

        judicial.parts.RecomendationTabPanel.superclass.constructor.call(this, cfg);

        this.getRecomendationGrid().getStore().on({
            clear: function(store) { store.isLoaded = false },
            beforeload: function(store) { store.isLoaded = true }
        });
        
        this.on({
            scope: this,
            activate: function() {
                var vm = this;
                setTimeout(
                    function () {
                        if (!vm.getRecomendationGrid().getStore().isLoaded)
                            vm.getRecomendationGrid().getStore().reload();
                    }, 
                    500
                );
            }
        })
    }

})