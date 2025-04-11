Ext.ns('toolkit.questionario');

toolkit.questionario.Form = Ext.extend(
    Ext.Window,
    {
        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                'title': 'Questionário',
                'closable': true,
                'resizable': true,
                'modal': true,
                'width': '400',
                'border': false,
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

            toolkit.questionario.Form.superclass.constructor.call(this, cfg);
            this.add(this.getFormPanel());
            if(this.values) this.getFormPanel().getForm().setValues(this.values);
        },

        getFormPanel: function() {
            if(!this._formPanel)
                this._formPanel = new Ext.form.FormPanel({
                    'frame': true,
                    'labelAlign': 'top',
                    'items': [
                        {
                            'fieldLabel': 'Titulo',
                            'xtype': 'textfield',
                            'allowBlank': false,
                            'width':'350',
                            'name': 'titulo'
                        },
                        {
                            'fieldLabel': 'Descrição',
                            'xtype': 'textarea',
                            'allowBlank': true,
                            'width':'350',
                            'height':'200',
                            'name': 'descricao'
                        },
                        {
                            'fieldLabel': 'Data Início',
                            'xtype': 'datefield',
                            'format': 'd/m/Y',
                            'width':350,
                            'allowBlank': false,
                            'name': 'data_inicio'
                        },
                        {
                            'fieldLabel': 'Data Fim',
                            'xtype': 'datefield',
                            'format': 'd/m/Y',
                            'allowBlank': true,
                            'width':350,
                            'name': 'data_fim'
                        },
                        {
                            'fieldLabel': 'Ativo',
                            'xtype': 'checkbox',
                            'checked':true,
                            'name': 'ativo'
                        },
                        {
                            'fieldLabel': 'Único',
                            'xtype': 'checkbox',
                            'checked':true,
                            'name': 'unico'
                        }
                    ]
                });
        
            return this._formPanel;
        },

        getParams: function() {
            return this.params;
        },

        save: function() {
            var form = this.getFormPanel().getForm();
            //console.log(this.action);
            form.waitMsgTarget = this.getEl();
            form.submit({
                'url': toolkit.util.Normalize.controller_action('QQuestionario', this.action),
                'params': this.getParams(),
                'scope': this,
                'success': function(form, action) {
                    if(this.callback && this.callback.success)
                        this.callback.success.handler.call(this.callback.success.scope ? this.callback.success.scope : window);
                    this.destroy()
                },
                'failure': function(form, action) {
                    console.debug(action);

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
                'waitMsg': 'Salvando dados do questionário...'
            })
        }
        
    }
);