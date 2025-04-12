Ext.ns('toolkit.gep');

toolkit.gep.ConfiguradorComissao = Ext.extend(
    toolkit.widget.TabPanel,
    {
        constructor: function() {
            var cfg = {
                'title': 'Configurador de Comissão',
                'layout': 'border',
                'items': [
                this.getFatorComissaoGrid(),
                {
                    'region': 'south',
                    'height':300,
                    'split': true,
                    'layout': 'hbox',
                    'border': false,
                    'items': [
                    this.getIntegrantesComissaoGrid(),
                    ]
                }
                ]
            };

            toolkit.gep.ConfiguradorComissao.superclass.constructor.call(this, cfg);
            this.getIntegrantesComissaoGrid().disable();
           /* new Ext.LoadMask(this.getIntegrantesComissaoGrid().getEl(), {
                msg: 'Carregando dados...',
                store: this.getIntegrantesComissaoGrid().getStore()
            });*/

        },

        manageSelectComissao: function() {
            var sel = this.getFatorComissaoGrid().getSelectionModel().getSelected();

            if(sel) {
                // console.log(sel.get('pk'));

                this.getIntegrantesComissaoGrid().enable();
                this.getIntegrantesComissaoGrid().getStore().baseParams = {
                    'pk_comissao': sel.get('pk'),
                    // 'pk_questionario': sel.get('pk_questionario')
                };

                new Ext.LoadMask(this.getIntegrantesComissaoGrid().getEl(), {
                    msg: 'Carregando dados...',
                    store: this.getIntegrantesComissaoGrid().getStore()
                });

                this.getIntegrantesComissaoGrid().getStore().load({});

               /* this.getIntegrantesComissaoGrid().getStore().load({
                    params:{
                        'pk_fator': sel.get('pk'),
                        'pk_questionario': sel.get('pk_questionario')
                    }
                });
                */
            }
            else {
                this.getIntegrantesComissaoGrid().disable();
                this.getIntegrantesComissaoGrid().getStore().baseParams = {};
                this.getIntegrantesComissaoGrid().getStore().removeAll();
            }
        },

        getFatorComissaoGrid: function() {
            if(!this._fatorAvaliacaoGrid) {
                this._fatorAvaliacaoGrid = new toolkit.gep.Comissao({
                    'region': 'center',
                    'bodyStyle': 'border-left:none',
                    'sm': new Ext.grid.RowSelectionModel({
                        'listeners': {
                            'scope': this,
                            'rowselect': this.manageSelectComissao
                        }
                    })
                });

            }
            return this._fatorAvaliacaoGrid;
        },

        getIntegrantesComissaoGrid: function() {
            if(!this._quesitoAvaliacaoGrid) {
                this._quesitoAvaliacaoGrid = new toolkit.gep.IntegrantesComissao({    
                    'region': 'center',
                    'flex':1,
                    'layout':'fit',
                    'height':'300',
                    'minHeight':'300',
                    'bodyStyle': 'border-right:none',
                });
            }
        
            return this._quesitoAvaliacaoGrid;
        },

        
    }
);