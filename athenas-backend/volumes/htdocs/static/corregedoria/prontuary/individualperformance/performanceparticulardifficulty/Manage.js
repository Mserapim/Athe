Ext._define('corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Manage', {
    extend: 'Ext.Window',

    getDetailPerformanceParticularDifficultyGrid: function(cfg) {
        if(!this._detailPerformanceParticularDifficultyGrid) {
            this._detailPerformanceParticularDifficultyGrid = Ext._create('corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Grid', {
                layout: 'form',
                border: true,
                gridAutoLoad: true,
                height: 520,
                columnAction: false,
                hideItemsToolbar:['download', '-', 'search'],
                params: {performanceparticulardifficulty: cfg.values.performanceparticulardifficulty, active: true, prontuary: cfg.values.prontuary, employee_id: cfg.values.employee_id},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                doubleClickHandler: function(grid) { },
           });
           this._detailPerformanceParticularDifficultyGrid.setFilterProperty('performanceparticulardifficulty_id', cfg.values.performanceparticulardifficulty, 100);
           this._detailPerformanceParticularDifficultyGrid.getStore().on({
               scope: this,
               load: function(sel) {
                   this.observerDetailPerformanceParticularDifficulty();
                   this._detailPerformanceParticularDifficultyGrid.getSelectionModel().clearSelections();
               },
           });
           this._detailPerformanceParticularDifficultyGrid.getSelectionModel().on({
               scope: this,
               selectionchange: function(sel) {
                   var selection = sel.getSelections();
                   if(selection.length == 1){
                       this.observerDetailPerformanceParticularDifficulty(selection[0].get('pk'));
                   }
               }
           });
       }
       return this._detailPerformanceParticularDifficultyGrid;
    },

    getTilePanel: function() {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                split: true,
                papperModel: 'card',
            });
        return this._tilePanel;
    },

    detailperformanceparticulardifficulty: function(value, dispatch) {
        this._detailPerformanceParticularDifficulty = value;
        return this._detailPerformanceParticularDifficulty;
    },

    observerDetailPerformanceParticularDifficulty: function(value) {
        if(value) {
            this.readView(value);
        }
        else {
            this.getTilePanel().disable();
            this.getTilePanel().setPageContent('');
        }
    },

    readView: function(detailperformanceparticulardifficulty) {
        var mask = new Ext.LoadMask(this.getTilePanel().getEl(), {msg: 'Carregado informações...'});
        var rest = Ext._create('corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Restful');
        mask.show();
        this.getTilePanel().enable();
        this.getTilePanel().setPageContent('');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document'),
            scope: this,
            autoAbort: true,
            params: {
                detailperformanceparticulardifficulty: detailperformanceparticulardifficulty
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
                                    this.getDetailPerformanceParticularDifficultyGrid(cfg),
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
        corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Manage.superclass.constructor.call(this, cfg);
        this.observerDetailPerformanceParticularDifficulty();
    }

});
