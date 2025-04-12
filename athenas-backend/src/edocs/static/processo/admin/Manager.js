/**
 *
 **/
Ext._define('edocs.processo.admin.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getAdminGrid: function() {
        if(!this._adminGrid) {
            this._adminGrid = Ext._create('edocs.processo.admin.processoAdminGrid', {
                // region: 'center',
                flex: 1,
                // flex: 0.5
                // split: true,
            });


            this._adminGrid.getSelectionModel().on({
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

         return this._adminGrid;
    },

    cleanTilePanel: function() {
        this.getTilePagePanel().disable();
        this.getTilePagePanel().setPageContent();
    },

    getDetail: function() {
        if(!this._detail)
            this._detail = Ext._create('Ext.Panel', {
                title:'Visualizar Detalhes',
                border: true,
                flex: 0.5,
            });

        return this._detail;
    },

    getTilePagePanel: function() {
        if(!this._tilePagePanel)
            this._tilePagePanel = Ext._create('core.TilePagePanel', {
                // region: 'center',
                flex: 1,
                disabled: true,
            });

        return this._tilePagePanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Processos'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'vbox',
                layoutConfig: {
                    align: 'stretch',
                },
                items: [
                    this.getAdminGrid(),
                    this.getTilePagePanel()
                ]
            }
        );
        edocs.processo.admin.Manager.superclass.constructor.call(this, cfg);
    }
});
