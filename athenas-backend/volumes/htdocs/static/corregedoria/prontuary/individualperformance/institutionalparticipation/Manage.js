Ext._define('corregedoria.prontuary.individualperformance.institutionalparticipation.Manage', {
    extend: 'Ext.Window',

    getDetailInstitutionalParticipationGrid: function(cfg) {
        if(!this._detailInstitutionalParticipationGrid)
            this._detailInstitutionalParticipationGrid = Ext._create('corregedoria.prontuary.individualperformance.institutionalparticipation.Grid', {
                layout: 'form',
                border: true,
                gridAutoLoad: true,
                height: 520,
                columnAction: false,
                hideItemsToolbar:['download', '-', 'search'],
                params: {institutionalparticipation: cfg.values.institutionalparticipation, active: true},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                doubleClickHandler: function(grid) { },
           });
           this._detailInstitutionalParticipationGrid.setFilterProperty('institutionalparticipation_id', cfg.values.institutionalparticipation, 100);
           this._detailInstitutionalParticipationGrid.getStore().on({
               scope: this,
               load: function(sel) {
                   this.observerDetailInstituionalParticipation();
                   this._detailInstitutionalParticipationGrid.getSelectionModel().clearSelections();
               },
           });
           this._detailInstitutionalParticipationGrid.getSelectionModel().on({
               scope: this,
               selectionchange: function(sel) {
                   var selection = sel.getSelections();
                   if(selection.length == 1){
                       this.observerDetailInstituionalParticipation(selection[0].get('pk'));
                   }
               }
           });
        return this._detailInstitutionalParticipationGrid;
    },

    getTilePanel: function() {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                split: true,
                papperModel: 'card',
            });
        return this._tilePanel;
    },

    detailinstitutionalparticipation: function(value, dispatch) {
        this._detailListIndication = value;
        return this._detailListIndication;
    },

    observerDetailInstituionalParticipation: function(value) {
        if(value) {
            this.readView(value);
        }
        else {
            this.getTilePanel().disable();
            this.getTilePanel().setPageContent('');
        }
    },

    readView: function(detailinstitutionalparticipation) {
        var mask = new Ext.LoadMask(this.getTilePanel().getEl(), {msg: 'Carregado informações...'});
        var rest = Ext._create('corregedoria.prontuary.individualperformance.institutionalparticipation.Restful');
        mask.show();
        this.getTilePanel().enable();
        this.getTilePanel().setPageContent('');
        Ext.Ajax.request({
            url: core.callAction(rest.resource, 'renderer_document'),
            scope: this,
            autoAbort: true,
            params: {
                detailinstitutionalparticipation: detailinstitutionalparticipation
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
                                    this.getDetailInstitutionalParticipationGrid(cfg),
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
            title: 'Desempenho Individual - Integrar Grupo de Trabalho, Comissão ou Comitê no âmbito da Instituição - Prontuário Individual: ' + cfg.values.employee_nome,
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
        corregedoria.prontuary.individualperformance.institutionalparticipation.Manage.superclass.constructor.call(this, cfg);
        this.observerDetailInstituionalParticipation();
    }

});
