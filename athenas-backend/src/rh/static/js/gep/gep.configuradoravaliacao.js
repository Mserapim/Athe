Ext.ns('toolkit.gep');

toolkit.gep.ConfiguradorAvaliacao = Ext.extend(
    toolkit.widget.TabPanel,
    {
        manageSelectFatorAvaliacao: function() {
            var sel = this.getFatorAvaliacaoGrid().getSelectionModel().getSelected();
            if(sel) {
                this.getQuesitoAvaliacaoGrid().enable();
                this.getQuesitoAvaliacaoGrid().getStore().baseParams = {
                    'pk_fator': sel.get('pk'),
                    'pk_questionario': sel.get('pk_questionario')
                };

                new Ext.LoadMask(this.getQuesitoAvaliacaoGrid().getEl(), {
                    msg: 'Carregando dados...',
                    store: this.getQuesitoAvaliacaoGrid().getStore()
                });

                this.getQuesitoAvaliacaoGrid().getStore().load({});

               /* this.getQuesitoAvaliacaoGrid().getStore().load({
                    params:{
                        'pk_fator': sel.get('pk'),
                        'pk_questionario': sel.get('pk_questionario')
                    }
                });
                */
            }
            else {
                this.getQuesitoAvaliacaoGrid().disable();
                this.getQuesitoAvaliacaoGrid().getStore().baseParams = {};
                this.getQuesitoAvaliacaoGrid().getStore().removeAll();
            }
        },

        getFatorAvaliacaoGrid: function() {
            if(!this._fatorAvaliacaoGrid) {
                this._fatorAvaliacaoGrid = new toolkit.gep.FatorAvaliacao({
                    'region': 'center',
                    'bodyStyle': 'border-left:none',
                    'sm': new Ext.grid.RowSelectionModel({
                        'listeners': {
                            'scope': this,
                            'rowselect': this.manageSelectFatorAvaliacao
                        }
                    })
                });

            }
            return this._fatorAvaliacaoGrid;
        },

        getQuesitoAvaliacaoGrid: function() {
            if(!this._quesitoAvaliacaoGrid) {
                this._quesitoAvaliacaoGrid = new toolkit.gep.QuesitoAvaliacao({    
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

        constructor: function() {
            var cfg = {
                'title': 'Configurador de Avaliação',
                'layout': 'border',
                'items': [
                this.getFatorAvaliacaoGrid(),
                {
                    'region': 'south',
                    'height':300,
                    'split': true,
                    'layout': 'hbox',
                    'border': false,
                    'items': [
                    this.getQuesitoAvaliacaoGrid(),
                    ]
                }
                ]
            };

            toolkit.gep.ConfiguradorAvaliacao.superclass.constructor.call(this, cfg);
            this.getQuesitoAvaliacaoGrid().disable();
           /* new Ext.LoadMask(this.getQuesitoAvaliacaoGrid().getEl(), {
                msg: 'Carregando dados...',
                store: this.getQuesitoAvaliacaoGrid().getStore()
            });*/

        }
    }
    );