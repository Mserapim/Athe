Ext.ns('toolkit.questionario');


toolkit.questionario.GerenciaQuestionario = Ext.extend(
    toolkit.widget.TabPanel,
    {
        manageSelectQuestionario: function() {
            var sel = this.getQuestionarioGrid().getSelectionModel().getSelected();
            if(sel && sel.get('ativo')!=0) {
                this.getElementoQuestionarioGrid().enable();
                this.getElementoQuestionarioGrid().getStore().baseParams = {
                    'questionario': sel.get('pk')
                };
                this.getElementoQuestionarioGrid().getStore().load({});
                this.getElementoQuestionarioGrid().getParams(sel.get('pk'));
                
            }
            else {
                this.getAlternativaGrid().disable();
                this.getAlternativaForm().disable();
                this.getElementoQuestionarioGrid().disable();
                this.getElementoQuestionarioGrid().getStore().baseParams = {};
                this.getElementoQuestionarioGrid().getStore().removeAll();
            }
        },

        manageSelectAlternativa: function() {
            var sel = this.getElementoQuestionarioGrid().getSelectionModel().getSelected();

            if(sel && sel.get('tipo')!='Ref. Textual' && sel.get('tipo')!= 'Questão Aberta') {
                this.getAlternativaGrid().enable();
                this.getAlternativaGrid().getStore().baseParams = {
                    'questao': sel.get('pk')
                };
                this.getAlternativaGrid().getStore().load({});
            }
            else {
                this.getAlternativaGrid().disable();
                this.getAlternativaGrid().getStore().baseParams = {};
                this.getAlternativaGrid().getStore().removeAll();
            }
        },

        /*manageSelectAlternativa: function() {
            var sel = this.getElementoQuestionarioGrid().getSelectionModel().getSelected();
            var lm = new Ext.LoadMask(this.getAlternativaForm().getEl(), {
                'msg': 'Carregando alternativas...'
            })
            lm.show();
            //console.log(this.getAlternativaForm().getEl())
            if(sel){
                Ext.Ajax.request({
                    'url': toolkit.util.Normalize.controller_action('QQuestao', 'get', [sel.get('pk')]),
                    'scope': this,
                    'success': function(request) {
                        var obj = Ext.decode(request.responseText);
                        this.getAlternativaForm().restoreBase = obj.instance;
                        //Só habilita o form de alternativa se for questao
                        if(obj.instance){
                            this.getAlternativaForm().params = { 'pk': obj.instance.pk };
                            this.getAlternativaForm().getForm().setValues(obj.instance);
                            this.getAlternativaForm().enable();
                            lm.hide();
                        }
                        else{ 
                            this.getAlternativaForm().getForm().setValues({
                                'alternativas':[]
                            });
                            this.getAlternativaForm().disable();
                        }
                        
                    },
                    'failure': function(request) {
                        Ext.Msg.show({
                            'title': 'Alternativas',
                            'msg': 'Não consegui obter informações sobre a alternativa selecionada.',
                            'icon': Ext.Msg.ERROR,
                            'buttons': Ext.Msg.OK
                        });
                        lm.hide();
                    }
                })
            }
            else {
                this.getAlternativaForm().getForm().setValues({
                    'alternativas':[]
                });
                this.getAlternativaForm().disable();
            }
        },*/

        getQuestionarioGrid: function() {
            if(!this._questionarioGrid) {
                this._questionarioGrid = new toolkit.questionario.QuestionarioGrid({
                    'region': 'center',
                    'bodyStyle': 'border-left:none',
                    'sm': new Ext.grid.RowSelectionModel({
                        'listeners': {
                            'scope': this,
                            'rowselect': this.manageSelectQuestionario
                        }
                    })
                });

                this._questionarioGrid.getStore().on('load', 
                    this.manageSelectQuestionario, 
                    this
                    );
            }
        
            return this._questionarioGrid;
        },

        getElementoQuestionarioGrid: function() {
            if(!this._elementoGrid) {
                this._elementoGrid = new toolkit.questionario.ElementoQuestionarioGrid({    
                    'region': 'center',
                    'flex':1,
                    'layout':'fit',
                    'height':'300',
                    'minHeight':'300',
                    'bodyStyle': 'border-right:none',
                    'sm': new Ext.grid.RowSelectionModel({
                        'listeners': {
                            'scope': this,
                            //'rowselect': this.manageSelectAlternativa
                            'rowselect': this.manageSelectAlternativa
                        }
                    })
                });

                this._elementoGrid.getStore().on('load', 
                    // this.manageSelectAlternativa, 
                    this.manageSelectAlternativa, 
                    this
                    );
            }
        
            return this._elementoGrid;
        },

        getAlternativaGrid: function() {
            if(!this._alternativaGrid) {
                this._alternativaGrid = new toolkit.questionario.AlternativaGrid({
                    'region': 'south',
                    'flex':1,
                    'layout':'fit',
                    'height':'300',
                    'minHeight':'300',
                    'bodyStyle': 'border-right:none',
                    'split': true

                });
            }
        
            return this._alternativaGrid;
        },

        getAlternativaForm: function() {
            if(!this._alternativaForm)
                this._alternativaForm = new toolkit.questionario.AlternativaGrid({
                    'region': 'south',
                    'flex': 1,
                    'layout':'fit',
                    'bodyStyle': 'border-right:none',
                    'split': true,
                    'height': 300,
                    'minHeight': 300,
                    'maxHeight': 300 
                });
        
            return this._alternativaForm;
        },

        constructor: function() {
            var cfg = {
                'title': 'Gerência de Questionário',
                'layout': 'border',
                'items': [
                this.getQuestionarioGrid(),
                {
                    'region': 'south',
                    'height':300,
                    'split': true,
                    'layout': 'hbox',
                    'border': false,
                    'items': [
                    this.getElementoQuestionarioGrid(),
                    //this.getAlternativaForm()
                    this.getAlternativaGrid()
                    ]
                }
                ]
            };

            toolkit.questionario.GerenciaQuestionario.superclass.constructor.call(this, cfg);
        }
    }
    );

