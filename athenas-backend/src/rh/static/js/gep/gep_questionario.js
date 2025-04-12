Ext.ns('toolkit.gep');

toolkit.gep.MontaQuestionarioAlteracao = Ext.extend(

    Ext.Window,
    {
        retorno:null,

        constructor: function(cfg, questoes,titulo_questionario){
            this.questoes = questoes;
            this.titulo_questionario = titulo_questionario;
            if(this.titulo_questionario==undefined)
                this.titulo_questionario='';
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                'layout':'fit',
                'width': 600,
                'height': 570,
                'closable':true,
                'autoScroll': true,
                'items':this.getFormPanel(),
                'buttons': [
                {
                    'text': 'Salvar',
                    'scope': this,
                    'handler': this.save
                },
                {
                    'text': 'Cancelar',
                    'scope': this,
                    'handler': this.destroy
                }
                ]   
            });

            toolkit.gep.MontaQuestionarioAlteracao.superclass.constructor.call(this, cfg);
        },

        createQuestionario: function(){
            var items = [];
            items[items.length] = {
                'xtype':'displayfield',
                'hideLabel':true,
                'value': '<b><font size="4">'+this.titulo_questionario + '</font></b><br><br>'
            };

            Ext.each(this.questoes, function(questao){
                var chave = questao.chave
                
                var el = {};
                if (questao.tipo == 'Questão Aberta')
                {
                    el = {
                        'xtype':'ckeditor',
                        'hideLabel':true,
                        'height':100,
                        // 'disabled':true,
                        'autoWidth':true,
                        'name': questao.label+':'+chave+':'+questao.id_questionario+':' + questao.id_questionario_resposta + ':'+questao.id,
                        'value': questao.texto_resposta
                    };
                }
                else if(questao.tipo == 'Questão Enum')
                {
                    var alts = [];
                    Ext.each(this.alternativas, function(alt){
                   
                        alts[alts.length]= {
                            'xtype':'textfield',
                            'fieldLabel':alt.label+ ' '+alt.texto,
                            'width':30,
                            'maxLength': 4,
                            'labelAlign':'left',
                            'maxLengthText':'Insira no máximo quatro digitos',
                            'name': questao.label+':'+chave+':'+questao.id_questionario+':' + questao.id_questionario_resposta + ':'+questao.id+':'+alt.id,
                            'value': questao.texto_resposta
                        }
                    });
                   
                    el = alts;
                }
                else if(questao.tipo == 'Questão MS')
                {
                    var alts = [];
                    console.log('asdf');
                    Ext.each(this.alternativas, function(alt){
                        alts[alts.length] = {
                            'boxLabel': alt.label+ ' '+alt.texto, 
                            'allowBlank':false,
                            'name': questao.label+':'+chave+':'+questao.id_questionario+':' + questao.id_questionario_resposta + ':'+questao.id,
                            'inputValue':alt.id,
                            'checked':(alt.id_resposta != undefined ? true : false)
                        };
                    });
                    if(questao.mista==true)
                    {
                        alts[alts.length] = {
                            'xtype': 'ckeditor',
                            'hideLabel':true,
                            'height':100,
                            'autoWidth':true,
                            'name': questao.label+':'+chave+':'+questao.id_questionario+':' + questao.id_questionario_resposta + ':'+questao.id,
                            'value': questao.texto_resposta
                        };
                    }
                    if(alts.length>0)
                    {
                        el = {
                            'xtype':'checkboxgroup',
                            'hideLabel':true,
                            'columns': 1,
                            'items': alts
                        }
                    }
                }
                else if (questao.tipo == 'Questão')
                {
                    var alts = [];
                    Ext.each(this.alternativas, function(alt){
                        alts[alts.length] = {
                            // 'disabled':true,
                            'boxLabel': alt.label+ ' '+alt.texto, 
                            'name': questao.label+':'+chave+':'+questao.id_questionario+':' + questao.id_questionario_resposta + ':'+questao.id,
                            'inputValue':alt.id,
                            'checked':(alt.id_resposta != undefined ? true : false)
                        };
                    });
                    if(questao.mista==true)
                    {
                        alts[alts.length] = {
                            'xtype': 'ckeditor',
                            'hideLabel':true,
                            'height':100,
                            'autoWidth':true,
                            'name': questao.label+':'+chave+':'+questao.id_questionario+':' + questao.id_questionario_resposta + ':'+questao.id,
                            'value': questao.texto_resposta
                        };
                    }
                    if(alts.length>0)
                    {
                        el = {
                            'xtype':'radiogroup',
                            'hideLabel':true,
                            'columns': 1,
                            'items': alts
                        }
                    }
                }

                if(questao.tipo == 'Ref. Textual')
                {    
                    items[items.length] = {
                        'xtype':'displayfield',
                        'labelAlign': 'top',
                        'hideLabel':true,
                        'value':'<b>'+this.label_ele+ ' - '+ this.label+'<br><i>'+this.conteudo+'</i></b><br>',
                    };
                }else {
                    items[items.length] = {
                        'xtype':'fieldset',
                        'hideLabel':true,
                        'title': questao.label+' - '+questao.enunciado,
                        'items':[el]
                    };
                }
            })
            return items;
        },

        getFormPanel: function() {
            if(!this._formPanel)
                this._formPanel = new Ext.form.FormPanel({
                    'frame': true,
                    'hideLabel':true,
                    'autoWidth':true,
                    'autoScroll':true,
                    'items': this.createQuestionario()
                });
        
            return this._formPanel;
        },

        getParams: function() {
            return this.params;
        },

        save: function() {

            Ext.Msg.show({
                'title': 'Atenção',
                'msg': 'Tem certeza que deseja finalizar? Verifique se preencheu corretamente o questionário antes de concluir. ',
                'icon': Ext.Msg.QUESTION,
                'buttons': Ext.Msg.YESNO,
                'scope': this,
                'fn': function(b) {
                    if(b == 'no') return;

                    var form = this.getFormPanel().getForm();
                    form.waitMsgTarget = this.getEl();
                    form.submit({
                        'url': toolkit.util.Normalize.controller_action('QMontarQuestionario', this.action),
                        'params': this.getParams(),
                        'scope': this,
                        'success': function(form, action) {
                            // console.log(action.result.data);
                            this.retorno = action.result.data;
                            Ext.Msg.alert('Sucesso', 'Dados salvos com sucesso!');
                            if(this.callback && this.callback.success)
                                this.callback.success.handler.call(this.callback.success.scope ? this.callback.success.scope : window);
                            this.destroy()
                        },
                        'failure': function(form, action) {
                            var message = ''
                            if(action.failureType == 'connect')
                                message = 'Não consegui acessar o recurso no servidor.'
                            else
                                message = action.result.message
                            Ext.Msg.show({
                                'title': 'Questionário',
                                'msg': message,
                                'icon': Ext.Msg.ERROR,
                                'buttons': Ext.Msg.OK
                            });

                            if(this.callback && this.callback.failure)
                                this.callback.failure.handler.call(this.callback.failure.scope ? this.callback.failure.scope : window);
                        },
                        'waitMsg': 'Salvando dados...'
                    })
                }
            });


        }
      
    }
    );