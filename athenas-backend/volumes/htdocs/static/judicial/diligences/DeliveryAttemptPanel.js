Ext._define('judicial.diligences.DeliveryAttemptPanel', {
    extend: 'Ext.Panel',
    
    getDiligenceGrid: function(cfg) {
        throw 'Método não implementado, judicial.diligences.DeliveryAttemptPanel é uma classe abstrata.';
    },
    
    getDeliveryGrid: function(cfg) {
        if(!this._deliveryGrid) {
            this._deliveryGrid = Ext._create('judicial.diligences.DeliveryAttemptGrid', {
                title: 'Tentativas de Entrega',
                region: 'center',
                height: 250,
                enabled: false,
                columnAction: false,
                gridAutoLoad: false,
            });
    
            this._deliveryGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
    
                    if(selection.length > 0)
                        this.delivery(selection[0]);
                    else
                        this.delivery(null);
                }
            });
    
        }
    
        return this._deliveryGrid;
    },
    
    delivery: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
    
        if(value !== undefined) {
            this._delivery = value;
    
            if(dispatch)
                this.deliveryObserve();
        }
    
        return this._delivery;
    },
    
    deliveryObserve: function() {
        var value = this.delivery();
        
        this.getTilePanel().setPageContent('');
    
        if(value) {
            var rest = Ext._create('judicial.diligences.DeliveryAttemptRestful');
            var mask = new Ext.LoadMask(this.getTilePanel().getEl(), {msg: 'carregando documento...'});
            
            mask.show();
            rest.rendered(
                value.get('pk'), 
                {
                    scope: this,
                    fn: function(rst) {
                        if(rst.success) 
                            this.getTilePanel().setPageContent(rst.rendered);
                        else {
                            this.getTilePanel().setPageContent('');
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
                        this.getTilePanel().setPageContent('');
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
    
    getDeliveryControlPanel: function(cfg) {
        if(!this._deliveryControlPanel)
            this._deliveryControlPanel = Ext._create('Ext.Panel', {
                region: 'east',
                minWidth: 830,
                width: 830,
                split: true,
                layout: {
                    type: 'vbox',
                    align: 'stretch',
                },
                items: [
                    this.getDeliveryGrid(cfg),
                    this.getTilePanel(cfg),
                ]
            });
    
        return this._deliveryControlPanel;
    },
    
    diligence: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
    
        if(value !== undefined) {
            this._diligence = value;
    
            if(dispatch)
                this.diligenceObserve();
        }
    
        return this._diligence;
    },
    
    diligenceObserve: function() {
        var value = this.diligence();
    
        if(value) {
            this.getDeliveryControlPanel().enable();
            this.getDeliveryGrid().setParam('diligence', value);
            this.getDeliveryGrid().setFilterProperty('diligence', value, 101);
        }
        else {
            this.getDeliveryControlPanel().disable();
            this.getDeliveryGrid().setParam('diligence', 0);
            this.getDeliveryGrid().setFilterProperty('diligence', 0, 101);
        }
        
        this.deliveryObserve();
    },
    
    configurePanel: function(cfg) {
        cfg = cfg || {};
        cfg.listeners = (cfg.listeners || {});
        
        Ext.applyIf(cfg.listeners, {
            added: function(panel) { panel.diligenceObserve(); }
        });
        
        Ext.apply(cfg, {
            border: false,
            layout: 'border',
            items: [
                this.getDiligenceGrid(cfg),
                this.getDeliveryControlPanel(cfg),
            ]
        })
        
        return cfg;
    }
})