Ext._define('corregedoria.prontuary.functionalperformance.inspectionlink.Manage', {
    extend: 'Ext.Window',

    getInspectionLinkGrid: function(cfg) {
        if(!this._inspectionLinkGrid)
            this._inspectionLinkGrid = Ext._create('corregedoria.prontuary.functionalperformance.inspectionlink.Grid', {
                layout: 'form',
                border: true,
                gridAutoLoad: true,
                height: 520,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {prontuary: cfg.values.prontuary, employee_id: cfg.values.employee_id},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                doubleClickHandler: function(grid) {
                    var selected = grid.getSelectionModel().getSelected();
                    var mask = new Ext.LoadMask(this.getEl(), {msg: 'Escrevendo no Prontuário Individual...'});
                    Ext.Msg.show({
                        title: 'Desempenho Funcional - Inspeções/Correições - Prontuário Individual',
                        msg: 'Deseja selecionar a inspeção para o prontuário?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        scope: this,
                        fn: function(btn) {
                            if(btn=='no') return;
                            mask.show();
                            Ext.Ajax.request({
                                scope: this,
                                url: core.callAction('PRONTUARYInspectionLink', 'mark_inspection'),
                                callback: function() {
                                    grid.getStore().reload();
                                },
                                success: function(request) {
                                    var rst = Ext.decode(request.responseText);
                                    if (rst.success == true) {
                                        mask.hide();
                                    } else {
                                        Ext.Msg.show({
                                            title: 'Desempenho Funcional - Inspeções/Correições - Prontuário Individual',
                                            msg: rst.message,
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        });
                                    }
                                },
                                failure: function(request) {
                                    var rst = Ext.decode(request.responseText);
                                    Ext.Msg.show({
                                        title: 'Desempenho Funcional - Inspeções/Correições - Prontuário Individual',
                                        msg: rst.message,
                                        icon: Ext.Msg.ERROR,
                                        buttons: Ext.Msg.OK
                                    });
                                },
                                params: { 'inspectionlink': selected.get('pk') },
                            });
                        }
                    });
                },
           });
           this._inspectionLinkGrid.setFilterProperty('prontuary_id', cfg.values.prontuary, 100);
           this._inspectionLinkGrid.getStore().on({
               scope: this,
               load: function(sel) {
                   this.observerInspectionLink();
                   this._inspectionLinkGrid.getSelectionModel().clearSelections();
               },
           });
           this._inspectionLinkGrid.getSelectionModel().on({
               scope: this,
               selectionchange: function(sel) {
                   var selection = sel.getSelections();
                   if(selection.length == 1){
                       this.observerInspectionLink(selection[0].get('pk'));
                   }
               }
           });
        return this._inspectionLinkGrid;
    },

    getTilePanel: function() {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                split: true,
                papperModel: 'card',
            });
        return this._tilePanel;
    },

    inspectionLink: function(value, dispatch) {
        this._inspectionLink = value;
        return this._inspectionLink;
    },

    observerInspectionLink: function(value) {
        if(value) {
            this.readView(value);
        }
        else {
            this.getTilePanel().disable();
            this.getTilePanel().setPageContent('');
        }
    },

    readView: function(inspectionLink) {
        var mask = new Ext.LoadMask(this.getTilePanel().getEl(), {msg: 'Carregado informações...'});
        var rest = Ext._create('corregedoria.prontuary.functionalperformance.inspectionlink.Restful');
        // var rest = this.getInspectionLinkGrid(cfg).factoryRestful();
        mask.show();
        this.getTilePanel().enable();
        this.getTilePanel().setPageContent('');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document'),
            scope: this,
            autoAbort: true,
            params: {
                inspectionLink: inspectionLink
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
                                    this.getInspectionLinkGrid(cfg),
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
            title: 'Desempenho Funcional - Inspeções/Correições - Prontuário Individual: ' + cfg.values.employee_nome,
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
        corregedoria.prontuary.functionalperformance.inspectionlink.Manage.superclass.constructor.call(this, cfg);
        // this.getInspectionLinkGrid().setFilterProperty('prontuary_id', cfg.values.prontuary, 100);
        this.observerInspectionLink();
    }

});
