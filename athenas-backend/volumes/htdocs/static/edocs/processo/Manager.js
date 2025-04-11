/**
 *
 **/
Ext._define('edocs.processo.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getEntradaGrid: function(cfg) {
        if(!this._entradaGrid) {
             this._entradaGrid = Ext._create('edocs.processo.EntradaGrid', {
                father: this,
                title: 'Entrada',
                region: 'center',
                split: true,
                minWidth: 400,
                width:450,
                minHeight: 300,
                geral: cfg.geral,
                callback: this.callback,
                id: 'entradagrid'
            });


            this._entradaGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    // var selected = this.getSelectionModel().getSelected();
                    var selection = selm.getSelections();
                    if(selection.length > 0) {
                        // var pks = [];
                        // Ext.each(selection,function(item) {pks.push(item.get('id'));});
                        var rest = Ext._create('edocs.processo.Restful', {});
                        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando dados...'});

                        mask.show();
                        rest.rendererDocument(
                            selection[0].data.id,
                            {
                                scope: this,
                                fn: function(document) {

                                    this.getTilePagePanel().enable();
                                    this.getTilePagePanel().setPageContent(document.content);
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

                    } else {
                        this.cleanTilePanel();
                    }
                },
                rowdeselect: function(selm) {
                    this.cleanTilePanel();
                }

            });

        }

        return this._entradaGrid;
    },

    cleanTilePanel: function() {
        this.getTilePagePanel().disable();
        this.getTilePagePanel().setPageContent();
    },

    getSaidaGrid: function(cfg) {
        if(!this._saidaGrid) {
             this._saidaGrid = Ext._create('edocs.processo.SaidaGrid', {
                father: this,
                title: 'Saída',
                region: 'center',
                split: true,
                minWidth: 400,
                width:450,
                minHeight: 300,
                geral: cfg.geral,
                callback: this.callback,
                id: 'saidagrid'
            });


            this._saidaGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    var selection = selm.getSelections();
                    if(selection.length > 0) {
                        var rest = Ext._create('edocs.processo.Restful', {});
                        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando dados...'});

                        mask.show();
                        rest.rendererDocument(
                            selection[0].data.id,
                            {
                                scope: this,
                                fn: function(document) {

                                    this.getTilePagePanel().enable();
                                    this.getTilePagePanel().setPageContent(document.content);
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
                    } else {
                        this.cleanTilePanel();
                    }
                }
            });

        }

        return this._saidaGrid;
    },

    getDetail: function(cfg) {
        if(!this._detail)
            this._detail = Ext._create('edocs.processo.consulta.processDetailsPanel', {
                region: 'center',
            });
        return this._detail;
    },

    getBoxTabPanel: function(cfg) {
        if(!this._boxTabPanel)
            this._boxTabPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                region: 'north',
                split: true,
                height: 300,
                minHeight: 250,
                maxHeight: 650,
                tabPosition: 'bottom',
                items: [
                    this.getEntradaGrid(cfg),
                    this.getSaidaGrid(cfg)
                ]
            });

        return this._boxTabPanel;
    },


    getScopeTreePanel: function(cfg) {
        if(!this._scopeTreePanel) {
            this._scopeTreePanel = Ext._create('edocs.processo.ProcessScopeTree', {
                region: 'west',
                width: 350,
                maxWidth: 450,
                minWidth: 250,
                split: true,
                grid_entrada: this.getEntradaGrid(cfg),
                grid_saida: this.getSaidaGrid(cfg)
            });

        }

        return this._scopeTreePanel;
    },

    getTilePagePanel: function() {
        if(!this._tilePagePanel)
            this._tilePagePanel = Ext._create('core.TilePagePanel', {
                region: 'center',
                disabled: true,
            });

        return this._tilePagePanel;
    },

    location: function(value, observe) {
        observe = core.nullValue(observe, true);

        if(value !== undefined) {
            this._location = value;
            if(observe) this.observe();
        }

        return this._location;
    },

    typeBox: function(value, observe) {
        observe = core.nullValue(observe, true);

        if(value !== undefined) {
            this._type_lawsuit = value;
            if(observe) this.observe();
        }

        return this._type_lawsuit;
    },

    observe: function(cfg) {
        var enable = false;
        var needLoad = false;
        var needClear = false;
        var obj;
        if(this.location()) {

            tree = this.getScopeTreePanel(cfg);

            entrada = this.getEntradaGrid(cfg);
            saida = this.getSaidaGrid(cfg);
            entrada.setFilterProperty('lotacao_destino', this.location(), 1000);

            saida.setFilterProperty('lotacao_origem', this.location(), 1000);

            ob = this.getBoxTabPanel(cfg);
            ob.add(entrada);

            this.cleanTilePanel();
        }
        else {
            this.cleanTilePanel();
        }

        if(this.typeBox()) {
            if (this.typeBox() == 1 ) {

                ob = this.getBoxTabPanel(cfg);
                entrada = this.getEntradaGrid(cfg);
                ob.add(entrada);

            } else {
                ob = this.getBoxTabPanel(cfg);
                saida = this.getSaidaGrid(cfg);
                ob.add(saida);
            }
        }
        else {
            needClear = true;
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        this.callback = {
            success: {
                scope: this,
                fn: function() {
                    this.getEntradaGrid().getStore().load();
                    this.getSaidaGrid().getStore().load();
                }
            }
        };

        Ext.applyIf(
            cfg,
            {
                title: 'Caixa de Processos - E-PADM'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getScopeTreePanel(cfg),
                    {
                        region: 'center',
                        layout: 'border',
                        border: false,
                        items: [
                            this.getBoxTabPanel(cfg),
                            this.getTilePagePanel()
                        ]
                    }
                ]
            }
        );

        edocs.processo.Manager.superclass.constructor.call(this, cfg);

        this.getScopeTreePanel().getSelectionModel().on({
            scope: this,
            beforeselect: function(sm, node) {
                if(node.attributes.type == 'location') {
                    this.typeBox(null, false);
                    this.location(node.attributes.node);
                }
                else if(node.attributes.type == 'type_box') {
                    this.typeBox(node.attributes.value, false);
                    this.location(node.parentNode.attributes.node);
                }
            }
        });

        this.observe(cfg);
    }
});
