/**
 *
 **/

Ext._define('rh.gfp.estrutura_salarial.ModeloTabelaSalarialWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gfp.estrutura_salarial.ModeloTabelaSalarialRestful',

    width: 800,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: this.getTabPanel(),
                // submit_all_checks: true
            });

        return this._formPanel;
    },

    getTabPanel: function() {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                height: 400,
                border: false,
                activeTab: 0,
                deferredRender: false,
                items: [
                    this.getMainPanel(),
                    this.getReferenciasPanel(),
                ]
            });

        return this._tabPanel;
    },

    getMainPanel: function() {
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                defaults: {
                    width: 500
                },
                title: 'Geral',
                layout: 'form',
                items: [
                    {
                        fieldLabel: 'Título',
                        xtype: 'textfield',
                        name: 'titulo',
                        allowBlank: false
                    },{
                        fieldLabel: 'Horizontal',
                        xtype: 'textfield',
                        name: 'titulo_horizontal',
                        allowBlank: false
                    },{
                        fieldLabel: 'Vertical',
                        xtype: 'textfield',
                        name: 'titulo_vertical',
                        allowBlank: false
                    },{
                        fieldLabel: 'Labels Horizontal',
                        xtype: 'textfield',
                        name: 'labels_horizontal',
                        allowBlank: true,
                    },{
                        fieldLabel: 'Labels Vertical',
                        xtype: 'textfield',
                        name: 'labels_vertical',
                        allowBlank: true
                    },{
                        fieldLabel: 'Quant. Horizontal',
                        xtype: 'displayfield',
                        name: 'quantidade_horizontal',
                        allowBlank: false
                    },{
                        fieldLabel: 'Quant. Vertical',
                        xtype: 'displayfield',
                        name: 'quantidade_vertical',
                        allowBlank: false
                    },
                ]
            });

        return this._mainPanel;
    },

    getReferenciasPanel: function() {
        if(!this._referenciasPanel)
            this._referenciasPanel =Ext._create('rh.gfp.estrutura_salarial.ReferenciaNiveis2DGrid', {
                title: 'Referências',
                gridAutoLoad: false
            });

        return this._referenciasPanel;
    },

    getTabelaPanel: function(){
        if(!this._modeloPanel)
            this._modeloPanel = Ext._create('Ext.Panel', {
                frame: true,
                border: false,
                defaults: {
                    width: 750
                },
                title: 'Referências',
                layout: 'column',
                // items: this.getGridButtons(this.getFormPanel().getForm().findField('labels_vertical').value, this.getFormPanel().getForm().findField('labels_horizontal').value),
                items: this.getGridButtons(),
            });

        return this._modeloPanel;
    },

    _observe: function() {
        var grid;
        if(this.oId) {
            grid = this.getReferenciasPanel();
            grid.setParam('modelo_tabela', this.oId);
            grid.setFilterProperty('modelo_tabela', this.oId);
            grid.enable();

            // gridPeriodo = this.getTabPeriodo();
            // gridPeriodo.enable();
            // gridPeriodo.setParam('modelo_tabela', this.oId);
            // gridPeriodo.setFilterProperty('modelo_tabela__id', this.oId);
        }
        else {
            this.getReferenciasPanel().disable();
            // this.getTabPeriodo().disable();
        }
    },

    // getTabEncargoFinanceiro: function() {
    //     if(!this._tabEncargoFinanceiro)
    //         this._tabEncargoFinanceiro = Ext._create('rh.movimentacao.requisicao.EncargoFinanceiroGrid', {
    //             title: 'Encargo Financeiro',
    //             gridAutoLoad: false
    //         });
    //     return this._tabEncargoFinanceiro;
    // },

    // getTabPeriodo: function() {
    //     if(!this._tabPeriodo)
    //         this._tabPeriodo = Ext._create('rh.movimentacao.requisicao.PeriodoRequisicaoGrid', {
    //             title: 'Períodos',
    //             gridAutoLoad: false
    //         });
    //     return this._tabPeriodo;
    // },

    // createGridButtons: function(labels_horizontal, labels_vertical){
    //     var qtd_vertical = labels_vertical.length +1;
    //     // var qtd_vertical = this.values.labels_vertical.split('|').length +1;
    //     var qtd_horizontal = labels_horizontal.length +1;
    //     // var qtd_horizontal = this.values.labels_horizontal.split('|').length +1;
    //     var items = []
    //     var fator_h = 1 / qtd_horizontal;
    //     for(h = 0; h < qtd_horizontal; h++){
    //         var itemh = {
    //             columnWidth: fator_h,
    //             baseCls:'x-plain',
    //             // layout:'fit',
    //             defaults: {
    //                 autoWidth: true,
    //                 // xtype: 'button',
    //                 // anchor: '95%',
    //             },
    //             items :[],
    //             // bodyStyle:'background-color:red',
    //         };

    //         for(v = 0; v < qtd_vertical; v++){
    //             if(v == 0 && h == 0){
    //                 text = '';
    //             }else if(v == 0){
    //                 text = '<b>'+labels_horizontal[h-1]+'</b>';
    //             }else if(h == 0){
    //                 text = '<b>'+labels_vertical[v-1]+'</b>';
    //             }else{
    //                 text = labels_vertical[v-1]+labels_horizontal[h-1]+' : $ : $';
    //             }

    //             itemh.items.push({text: text,});
    //         }

    //         items.push(itemh);
    //     }
    //     return items;
    // },

    // getGridButtons: function(){
    //     var horizontal = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'], vertical = ['A', 'B', 'C'];
    //     var qtd_vertical = vertical.length +1;
    //     // var qtd_vertical = this.values.labels_vertical.split('|').length +1;
    //     var qtd_horizontal = horizontal.length +1;
    //     // var qtd_horizontal = this.values.labels_horizontal.split('|').length +1;
    //     var items = []
    //     var fator_h = 1 / qtd_horizontal;
    //     for(h = 0; h < qtd_horizontal; h++){
    //         var itemh = {
    //             columnWidth: fator_h,
    //             // baseCls:'x-plain',
    //             // layout:'fit',
    //             defaults: {
    //                 autoWidth: true,
    //                 height: 30,
    //                 style: 'margin: 0 auto'
    //                 // xtype: 'button',
    //                 // anchor: '95%',
    //             },
    //             items :[],
    //             // bodyStyle:'background-color:red',
    //         };

    //         for(v = 0; v < qtd_vertical; v++){
    //             if(v == 0 && h == 0){
    //                 text = '-/-';
    //             }else if(v == 0){
    //                 text = horizontal[h-1];
    //             }else if(h == 0){
    //                 text = vertical[v-1];
    //             }else{
    //                 text = vertical[v-1]+horizontal[h-1]+' : $ : $';
    //             }

    //             itemh.items.push({html: text,});
    //         }

    //         items.push(itemh);
    //     }
    //     return items;
    // },

    constructor: function(cfg){
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Modelo de Tabela Salarial'
            }
        );

        Ext.apply(
            cfg,
            {
                // layout: 'border',
                // items: this.getGrid()
            }
        );

        rh.gfp.estrutura_salarial.ModeloTabelaSalarialWindow.superclass.constructor.call(this, cfg);
        this.values && this.getFormPanel().getForm().setValues(this.values);
        this._observe();
    }
});
