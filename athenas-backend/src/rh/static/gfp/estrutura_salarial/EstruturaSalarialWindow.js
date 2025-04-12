Ext._define('rh.gfp.estrutura_salarial.EstruturaSalarialWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.estrutura_salarial.EstruturaSalarialRestful',

    width: 900,

    _observe: function() {
        var gridTabelas, gridReferencias, panelTabelas, panelCargosEstrutura;
        if(this.oId) {
            panelTabelas = this.getTabelasPanel();
            gridTabelas = this.getTabelasGrid();
            gridTabelas.setParam('estrutura_salarial', this.oId);
            gridTabelas.setFilterProperty('estrutura_salarial', this.oId);
            gridTabelas.setSortProperty('start_validity','DESC', false)
            panelTabelas.enable();

            gridReferencias = this.getReferenciasNiveis2D();
            gridReferencias.enable();
            gridReferencias.setParam('estrutura_salarial', this.oId);
            gridReferencias.setFilterProperty('estrutura_salarial', this.oId);
            gridReferencias.addSortProperty('ordem', 'ASC', false)

            panelCargosEstrutura = this.getCargosReferenciasPanel();
            gridCargosEstrutura = this.getCargosEstruturaGrid();
            gridCargosEstrutura.setParam('estrutura_salarial', this.oId);
            gridCargosEstrutura.setFilterProperty('estrutura_salarial', this.oId);
            panelCargosEstrutura.enable();

            // gridReferenciasCargos = this.getReferenciasForCargo();
            // // gridReferenciasCargos.enable();
            // gridReferenciasCargos.setParam('modelo_tabela', this.values.modelo_tabela);
            // gridReferenciasCargos.setFilterProperty('modelo_tabela', this.values.modelo_tabela);

        }
        else {
            this.getTabelasPanel().disable();
            this.getReferenciasNiveis2D().disable();
            this.getCargosReferenciasPanel().disable();
        }
    },

    getTabelasGrid: function(cfg){
        if(!this._tabelasGrid)
            this._tabelasGrid =Ext._create('rh.gfp.estrutura_salarial.TabelaSalarialGrid', {
                gridAutoLoad: false,
                region: 'center',
                layout: 'fit',
                hideColumns: ['estrutura_salarial_unicode', 'tabela_anterior_unicode'],
                hideItemsToolbar: ['edit', 'remove', ],
            });

        return this._tabelasGrid;
    },

    getTabelaSalariosGrid: function(cfg){
        if(!this._tabelaSalario){
            this._tabelaSalario = Ext._create('rh.gfp.estrutura_salarial.ReferenciaSalarioGrid', {
                gridAutoLoad: false,
                region: 'east',
                width: 270,
                disabled: true,
                columnAction: false,
                hideColumns: ['tabela_salarial_unicode', ],
                hideItemsToolbar: ['edit', 'remove', 'search', ],
            });
        }
        return this._tabelaSalario;
    },

    getTabelasPanel: function(cfg) {
        if(!this._tabelasPanel){
            this._tabelasPanel = Ext._create('Ext.Panel', {
                title: 'Tabelas Salariais',
                border: false,
                layout: 'border',
                items: [
                    this.getTabelasGrid(),
                    this.getTabelaSalariosGrid()
                ]
            });

            this.getTabelasGrid().getSelectionModel().on(
                'rowselect', function(sel, rIdx, rec){
                    console.debug('ROW SELECT:'+rec.data.pk);
                    gridReferenciasSalario = this.getTabelaSalariosGrid();
                    gridReferenciasSalario.setParam('tabela_salarial', rec.data.pk);
                    gridReferenciasSalario.setFilterProperty('tabela_salarial', rec.data.pk, 1, true);
                    gridReferenciasSalario.enable();
                    // gridReferenciasSalario.load();
                },
                this
            );

            this.getTabelasGrid().getSelectionModel().on(
                'rowdeselect', function(sel, rIdx, rec){
                    console.debug('ROW DESELECT');
                    gridReferenciasSalario.disable();
                },
                this
            );
        }
        return this._tabelasPanel;
    },

    getCargosEstruturaGrid:function(cfg){
        if(!this._cargosEstruturaGrid)
            this._cargosEstruturaGrid =Ext._create('rh.gfp.estrutura_salarial.CargosEstruturaGrid', {
                // title: 'Tabelas Salariais',
                region: 'center',
                layout: 'fit',
                gridAutoLoad: false,
                hideColumns: ['estrutura_salarial_unicode', 'publicacao_unicode'],
            });

        return this._cargosEstruturaGrid;
    },

    getReferenciasForCargo: function(cfg){
        if(!this._referenciasCargosField){
            this._referenciasCargosField = Ext._create('core.fields.RelatedRestfulField', {
                name: 'referencias',
                relatedname: 'cargos_estrutura',
                region: 'east',
                margins: '0 0 0 5',
                layout: 'fit',
                width: 200,
                height: 315,
                rest: 'rh.gfp.estrutura_salarial.CargosEstruturaRestful',
                sourceRest: 'rh.gfp.estrutura_salarial.ReferenciaNiveis2DRestful',
                preFilter: [
                    {
                        property: 'estrutura_salarial',
                        value: cfg.values.pk,
                        stage: 9999
                    }
                ],
                // oId: cfg.oId,
                disabled: true,
            });
        }
        return this._referenciasCargosField;
    },

    getCargosReferenciasPanel: function(cfg){
        if(!this._cargosReferencias){
            this._cargosReferencias = Ext._create('Ext.Panel', {
                title: 'Cargos/Referências',
                // height: 400,
                border: false,
                layout: 'border',
                // labelAlign: 'left',
                items: [
                    this.getCargosEstruturaGrid(cfg),
                    this.getReferenciasForCargo(cfg)
                ]
            });

            this.getCargosEstruturaGrid().getSelectionModel().on(
                'rowselect', function(sel, rIdx, rec){
                    console.debug('ROW SELECT:'+rec.data.pk);
                    gridReferenciasCargos = this.getReferenciasForCargo();
                    gridReferenciasCargos.objectId(rec.data.pk);
                    // gridReferenciasCargos.setParam('modelo_tabela', this.values.modelo_tabela);
                    // gridReferenciasCargos.setFilterProperty('modelo_tabela', this.values.modelo_tabela, 1, false);
                    // gridReferenciasCargos.setParam('cargos_estrutura', rec.data.pk);
                    // gridReferenciasCargos.setFilterProperty('cargos_estrutura', rec.data.pk, 2, true);
                    gridReferenciasCargos.enable();
                },
                this
            );

            this.getCargosEstruturaGrid().getSelectionModel().on(
                'rowdeselect', function(sel, rIdx, rec){
                    console.debug('ROW DESELECT');
                    gridReferenciasCargos.disable();
                },
                this
            );
        }
        return this._cargosReferencias;
    },

    getReferenciasNiveis2D: function(cfg){
        if(!this._referenciasNiveis2D){
            this._referenciasNiveis2D = Ext._create('rh.gfp.estrutura_salarial.ReferenciaNiveis2DGrid', {
                title: 'Referências Salariais',
                gridAutoLoad: false,
                hideColumns: ['estrutura_salarial_unicode', ],
            });

        }
        return this._referenciasNiveis2D;
    },

    getEstruturasRevogadasGrid: function(cfg){
        if(!this._estruturasRevogadasGrid){
            this._estruturasRevogadasGrid = Ext._create('rh.gfp.estrutura_salarial.EstruturaSalarialGrid', {
                title: 'Estruturas Revogadas',
                gridAutoLoad: false,
                // hideColumns: ['modelo_tabela_unicode', ],
            });

        }
        return this._estruturasRevogadasGrid;
    },

    getTabPanel: function(cfg) {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                height: 400,
                border: false,
                activeTab: 0,
                deferredRender: false,
                items: [
                    this.getEstruturaPanel(cfg),
                    this.getReferenciasNiveis2D(cfg),
                    this.getTabelasPanel(cfg),
                    this.getCargosReferenciasPanel(cfg),
                    // this.getEstruturasRevogadasGrid(cfg),
                ]
            });

        return this._tabPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                labelAlign: 'top',
                // title: 'Inner Tabs',
                bodyStyle:'padding:5px',
                // width: 800,
                items: this.getTabPanel(cfg),
            });

        return this._formPanel;
    },

    getEstruturaPanel: function() {
        if(!this._estruturaPanel)
            this._estruturaPanel = Ext._create('Ext.Panel', {
                labelAlign: 'top',
                // title: 'Inner Tabs',
                layout: 'form',
                bodyStyle:'padding:5px',
                title: 'Geral',
                items: [
                    {
                        layout:'column',
                        border:false,
                        items:[{
                            columnWidth:.10,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype:'textfield',
                                fieldLabel: 'Código',
                                name: 'codigo',
                                anchor:'95%'
                            },]
                        },{
                            columnWidth:.75,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype:'textfield',
                                fieldLabel: 'Título',
                                name: 'titulo',
                                anchor:'95%'
                            },]
                        },{
                            columnWidth:.15,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype: 'choicefield',
                                fieldLabel: 'Identificador',
                                name: 'identifier',
                                hiddenName: 'identifier',
                                choiceId: 'gfp.STRUCTURE_IDENTIFIER',
                                anchor:'95%'
                            }]
                        }]
                    },{
                        layout:'column',
                        border:false,
                        items:[{
                            columnWidth:.25,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype:'textfield',
                                fieldLabel: 'Formatacao',
                                name: 'formatacao',
                                anchor:'95%'
                            }]
                        },{
                            columnWidth:.55,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype: "rest-autocompletefield",
                                fieldLabel: "Publicação",
                                allowBlank: false,
                                rest: "rh.publicacao.Restful",
                                name: "publicacao"
                            }]
                        },{
                            columnWidth:.20,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype: 'choicefield',
                                fieldLabel: 'Unidade de salário',
                                name: 'salary_unit',
                                hiddenName: 'salary_unit',
                                choiceId: 'gfp.SALARY_UNIT',
                                anchor:'95%'
                            }]
                        }]
                    },{
                        layout:'column',
                        border:false,
                        items:[{
                            columnWidth:.25,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype:'numberfield',
                                fieldLabel: 'Progressão inicial',
                                name: 'meses_progressao_inicial',
                                anchor:'93%'
                            },]
                        },{
                            columnWidth:.25,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype:'numberfield',
                                fieldLabel: 'Progressões',
                                name: 'meses_progressao',
                                anchor:'93%'
                            },]
                        },{
                            columnWidth:.25,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype:'datefield',
                                fieldLabel: 'Início vigência',
                                name: 'data_vigencia_inicio',
                                anchor:'93%'
                            },]
                        },{
                            columnWidth:.25,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype:'datefield',
                                fieldLabel: 'Fim vigência',
                                name: 'data_vigencia_fim',
                                anchor:'93%'
                            },]
                        },]
                    },{
                        layout:'column',
                        border:false,
                        items:[{
                            columnWidth:.15,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype:'textfield',
                                fieldLabel: 'Título Vertical',
                                name: 'vertical_name',
                                anchor:'95%'
                            },]
                        },{
                            columnWidth:.15,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype:'textfield',
                                fieldLabel: 'Título Horizontal',
                                name: 'horizontal_name',
                                anchor:'95%'
                            },]
                        },{
                            columnWidth:.35,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype:'textfield',
                                fieldLabel: 'Níveis verticais',
                                name: 'vertical_labels',
                                anchor:'95%'
                            },]
                        },{
                            columnWidth:.35,
                            layout: 'form',
                            border:false,
                            items: [{
                                xtype:'textfield',
                                fieldLabel: 'Níveis horizontais',
                                name: 'horizontal_labels',
                                anchor:'95%'
                            },]
                        },]
                    },{
                        // layout: 'form',
                        fieldLabel: 'Descrição',
                        name: 'descricao',
                        xtype: 'textarea',
                        anchor: '96%'
                    }
                ],
            });

        return this._estruturaPanel;
    },

    constructor: function(cfg){
        cfg = cfg ? cfg : {};

        Ext.apply(
            cfg,
            {title: 'Estrutura Salarial', }
        );

        rh.gfp.estrutura_salarial.EstruturaSalarialWindow.superclass.constructor.call(this, cfg);
        this.values && this.getFormPanel().getForm().setValues(this.values);
        this._observe();

    }
});
