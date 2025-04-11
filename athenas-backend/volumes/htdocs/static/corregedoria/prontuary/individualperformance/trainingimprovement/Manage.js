Ext._define('corregedoria.prontuary.individualperformance.trainingimprovement.Manage', {
    extend: 'Ext.Window',

    getDetailTrainingImprovementGrid: function(cfg) {
        if(!this._detailTrainingImprovementGrid) {
            this._detailTrainingImprovementGrid = Ext._create('corregedoria.prontuary.individualperformance.trainingimprovement.Grid', {
                layout: 'form',
                border: true,
                gridAutoLoad: true,
                height: 520,
                columnAction: false,
                hideItemsToolbar:['download', '-', 'search'],
                params: {trainingimprovement: cfg.values.trainingimprovement, active: true, prontuary: cfg.values.prontuary, employee_id: cfg.values.employee_id},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                doubleClickHandler: function(grid) { },
           });
           this._detailTrainingImprovementGrid.setFilterProperty('trainingimprovement_id', cfg.values.trainingimprovement, 100);
           this._detailTrainingImprovementGrid.getStore().on({
               scope: this,
               load: function(sel) {
                   this.observerDetailTrainingImprovement();
                   this._detailTrainingImprovementGrid.getSelectionModel().clearSelections();
               },
           });
           this._detailTrainingImprovementGrid.getSelectionModel().on({
               scope: this,
               selectionchange: function(sel) {
                   var selection = sel.getSelections();
                   if(selection.length == 1){
                       this.observerDetailTrainingImprovement(selection[0].get('pk'));
                   }
               }
           });
       }
       return this._detailTrainingImprovementGrid;
    },

    getTilePanel: function() {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                split: true,
                papperModel: 'card',
            });
        return this._tilePanel;
    },

    detailtrainingimprovement: function(value, dispatch) {
        this._detailTrainingImprovement = value;
        return this._detailTrainingImprovement;
    },

    observerDetailTrainingImprovement: function(value) {
        if(value) {
            this.readView(value);
        }
        else {
            this.getTilePanel().disable();
            this.getTilePanel().setPageContent('');
        }
    },

    readView: function(detailtrainingimprovement) {
        var mask = new Ext.LoadMask(this.getTilePanel().getEl(), {msg: 'Carregado informações...'});
        var rest = Ext._create('corregedoria.prontuary.individualperformance.trainingimprovement.Restful');
        mask.show();
        this.getTilePanel().enable();
        this.getTilePanel().setPageContent('');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document'),
            scope: this,
            autoAbort: true,
            params: {
                detailtrainingimprovement: detailtrainingimprovement
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
                                    this.getDetailTrainingImprovementGrid(cfg),
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
            title: 'Desempenho Individual - Aprimoramento de Formação Jurídica e Profissional - Prontuário Individual: ' + cfg.values.employee_nome,
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
        corregedoria.prontuary.individualperformance.trainingimprovement.Manage.superclass.constructor.call(this, cfg);
        this.observerDetailTrainingImprovement();
    }

});
