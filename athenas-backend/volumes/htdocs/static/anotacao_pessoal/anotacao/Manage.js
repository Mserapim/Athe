/**
 *
 **/
Ext._define('anotacao_pessoal.anotacao.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getServidorGrid: function(cfg) {
        if(!this._servidor) {
            this._servidor = Ext._create('anotacao_pessoal.anotacao.servidor.Grid', {
                region: 'north', //'center',
                columnAction: false,
                allowCreate: false,
                allowUpdate: false,
                height: 200,
                split: true,
                tipos_anotacao: cfg.tipos_anotacao,
                tipos_documento: cfg.tipos_documento,
            });

            this._servidor.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data) {
                    this.observe(cfg, data.get('servidor_pk'));
                },
                rowdeselect: function() {
                    this.observe(cfg);
                }
            });
        }

        return this._servidor;
    },

    getAnotacaoGrid: function(cfg) {
        if(!this._subAnotacaoGrid) {
            this._subAnotacaoGrid = Ext._create('anotacao_pessoal.anotacao.anotacao_pessoal.Grid', {
                gridAutoLoad: false,
                region: 'center',
                disabled: true,
                flex: 1.0,
                border: false,
                tipos_anotacao: cfg.tipos_anotacao,
                tipos_documento: cfg.tipos_documento,
            });

            this._subAnotacaoGrid.getSelectionModel().on({
                scope: this,
                rowselect: function (sm, index, record) {
                    this.observeAnotacaoEvent(record);
                },
                rowdeselect: function (sm) {
                    this.observeAnotacaoEvent(null);
                }

            });

        }

        return this._subAnotacaoGrid;
    },

    observeAnotacaoEvent: function(record){
		if(record != null){	
            this.getTextoPanel().items.items[0].setValue(record.get('texto')) 
            this.getTextoPanel().enable();

		}
		else{
			this.getTextoPanel().disable();
            this.getTextoPanel().items.items[0].setValue('') 

		}
    },

    observe: function(cfg, value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._param = value;

            if(!prevent)
                this.observeAnotacao(cfg);
            
        }

        return this._param;
    },


    observeAnotacao: function(cfg){

        var value = this.observe();

        if(value) {
            this.getAnotacaoGrid(cfg).enable();
            this.getAnotacaoGrid(cfg).servidor = value;
            this.getAnotacaoGrid(cfg).setFilterProperty('servidor', value, 0, false);
            this.getAnotacaoGrid(cfg).setParam('servidor', value);
            this.getAnotacaoGrid(cfg).getStore().load();

        }
        else {
            this.getAnotacaoGrid(cfg).getStore().removeAll();
            this.getAnotacaoGrid(cfg).disable();
        }
    },

    getControlPanel: function () {
        if (!this._controlPanel)
            this._controlPanel = Ext._create('Ext.Panel', {
                width: 15,
                frame: true,
                layout: 'vbox',
                bodyStyle: {
                    'border-top': 0,
                    'border-bottom': 0
                },
            });
        return this._controlPanel;
    },

    getTextoPanel: function (cfg) {
        if (!this._textoPanel)
            this._textoPanel = Ext._create('Ext.Panel', {
                bodyStyle: {
                    'padding-top': 15,
                    'padding-right': 12
                },
                
                scroll: true,
                gridAutoLoad: false,
				disabled: true,
				flex: 1.0,
				border: false,
                frame: true,
                title: 'Texto',
                region: 'east',
                split: true,
                width: "50%",
                
                layout: 'fit',
                items: [
                  
                    {   
                        scroll: true,
                        columnWidth: .1,
                        xtype: 'htmleditor',
                        width: 1000,
                        height: 1000,
                        
                        enableAlignments: false,
                        enableColors: false,
                        enableFont: false,
                        enableFontSize: false,
                        enableFormat: false,
                        enableLinks: false,
                        enableLists: false,
                        enableSourceEdit: false,
                        value: '',
                    },
                    
                ]
            });
        return this._textoPanel;
    },




    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Cadastro de Anotações'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getServidorGrid(cfg),
                    

                    {

                        region: 'center',
                        layout: 'border',
                        minHeight: 150,
                        scope: this,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },






                        items: [
                            this.getAnotacaoGrid(cfg),
                            this.getControlPanel(),
                            this.getTextoPanel(),
                        ]
                    }

                ]
            }
        );

        anotacao_pessoal.anotacao.Manage.superclass.constructor.call(this, cfg);
    }
});
