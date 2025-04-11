Ext._define('corregedoria.prontuary.individualperformance.listindication.Manage', {
    extend: 'Ext.Window',

    getDetailListIndicationGrid: function(cfg) {
        if(!this._detailListIndicationGrid)
            this._detailListIndicationGrid = Ext._create('corregedoria.prontuary.individualperformance.listindication.Grid', {
                layout: 'form',
                border: true,
                gridAutoLoad: true,
                height: 520,
                columnAction: false,
                hideItemsToolbar:['download', '-', 'search'],
                params: {listindication: cfg.values.listindication, active: true},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                doubleClickHandler: function(grid) {
                    // var selected = grid.getSelectionModel().getSelected();
                    // var mask = new Ext.LoadMask(this.getEl(), {msg: 'Escrevendo no Prontuário Individual...'});
                    // Ext.Msg.show({
                    //     title: 'Desempenho Funcional - Inspeções/Correições - Prontuário Individual',
                    //     msg: 'Deseja selecionar a inspeção para o prontuário?',
                    //     icon: Ext.Msg.QUESTION,
                    //     buttons: Ext.Msg.YESNO,
                    //     scope: this,
                    //     fn: function(btn) {
                    //         if(btn=='no') return;
                    //         mask.show();
                    //         Ext.Ajax.request({
                    //             scope: this,
                    //             url: core.callAction('PRONTUARYDetailListIndication', 'mark_inspection'),
                    //             callback: function() {
                    //                 grid.getStore().reload();
                    //             },
                    //             success: function(request) {
                    //                 var rst = Ext.decode(request.responseText);
                    //                 if (rst.success == true) {
                    //                     mask.hide();
                    //                 } else {
                    //                     Ext.Msg.show({
                    //                         title: 'Desempenho Funcional - Inspeções/Correições - Prontuário Individual',
                    //                         msg: rst.message,
                    //                         icon: Ext.Msg.ERROR,
                    //                         buttons: Ext.Msg.OK
                    //                     });
                    //                 }
                    //             },
                    //             failure: function(request) {
                    //                 var rst = Ext.decode(request.responseText);
                    //                 Ext.Msg.show({
                    //                     title: 'Desempenho Funcional - Inspeções/Correições - Prontuário Individual',
                    //                     msg: rst.message,
                    //                     icon: Ext.Msg.ERROR,
                    //                     buttons: Ext.Msg.OK
                    //                 });
                    //             },
                    //             params: { 'inspectionlink': selected.get('pk') },
                    //         });
                    //     }
                    // });
                },
           });
           this._detailListIndicationGrid.setFilterProperty('listindication_id', cfg.values.listindication, 100);
           this._detailListIndicationGrid.getStore().on({
               scope: this,
               load: function(sel) {
                   this.observerDetailListIndication();
                   this._detailListIndicationGrid.getSelectionModel().clearSelections();
               },
           });
           this._detailListIndicationGrid.getSelectionModel().on({
               scope: this,
               selectionchange: function(sel) {
                   var selection = sel.getSelections();
                   if(selection.length == 1){
                       this.observerDetailListIndication(selection[0].get('pk'));
                   }
               }
           });
        return this._detailListIndicationGrid;
    },

    getTilePanel: function() {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                split: true,
                papperModel: 'card',
            });
        return this._tilePanel;
    },

    detaillistindication: function(value, dispatch) {
        this._detailListIndication = value;
        return this._detailListIndication;
    },

    observerDetailListIndication: function(value) {
        if(value) {
            this.readView(value);
        }
        else {
            this.getTilePanel().disable();
            this.getTilePanel().setPageContent('');
        }
    },

    readView: function(detaillistindication) {
        var mask = new Ext.LoadMask(this.getTilePanel().getEl(), {msg: 'Carregado informações...'});
        var rest = Ext._create('corregedoria.prontuary.individualperformance.listindication.Restful');
        // var rest = this.getDetailListIndicationGrid(cfg).factoryRestful();
        mask.show();
        this.getTilePanel().enable();
        this.getTilePanel().setPageContent('');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document'),
            scope: this,
            autoAbort: true,
            params: {
                detaillistindication: detaillistindication
            },
            callback: function() {
                mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                var me = this;
                if(rst.success) {
                    this.getTilePanel().setPageContent(rst.content);
                }
                else
                    Ext.Msg.show({
                        title: 'Carregando informações',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Carregando informações',
                    msg: 'Recurso indisponivel no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.50,
                                items: [
                                    this.getDetailListIndicationGrid(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                layout: 'form',
                                labelWidth: 1,
                                columnWidth: 0.50,
                                height: 520,
                                style: {marginLeft: '10px'},
                                items: [
                                    this.getTilePanel(cfg),
                                ]
                            },
                        ]
                    },
                ]
            });
        }
        return this._formPanel;
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                }
            ];
        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            title: 'Desempenho Individual - Indicação em Lista de Remoção e Promoção - Prontuário Individual: ' + cfg.values.employee_nome,
            width: 1400,
            height: 600,
            modal: true,
        });
        Ext.apply(cfg, {
            items: [
                this.getFormPanel(cfg),
            ],
            buttons: this.getButtons(cfg),
        });
        corregedoria.prontuary.individualperformance.listindication.Manage.superclass.constructor.call(this, cfg);
        // this.getDetailListIndicationGrid().setFilterProperty('prontuary_id', cfg.values.prontuary, 100);
        this.observerDetailListIndication();
    }

});
