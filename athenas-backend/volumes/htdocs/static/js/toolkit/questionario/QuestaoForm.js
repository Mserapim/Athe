Ext.ns('toolkit.questionario');

toolkit.questionario.QuestaoForm = Ext.extend(
    Ext.Window,
    {
        constructor: function(cfg , questionario) {
            this.questionario = questionario;
            
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                'title': 'Questão',
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

            toolkit.questionario.QuestaoForm.superclass.constructor.call(this, cfg);
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
                            xtype: 'combo',
                            width:350,
                            fieldLabel: 'Elemento Pai',
                            displayField: 'descricao',
                            valueField: 'pk',
                            store: new Ext.data.Store({
                                proxy: new Ext.data.HttpProxy({
                                    method: 'POST',
                                    disableCaching: false,
                                    url: toolkit.util.Normalize.controller_action('QElemento', 'get_elemento_pai'),
                                    autoLoad:true,
                                }),
                                baseParams: {
                                    pk_questionario: this.questionario
                                },
                                reader: new Ext.data.JsonReader({
                                    'idProperty': 'pk',
                                    'fields': [
                                        'pk', 'descricao'
                                    ],
                                    'root': 'collection',
                                    'totalProperty': 'count'
                                }),
                                autoLoad: true
                            }),
                            triggerAction: 'all',
                            mode: 'local',
                            hiddenName: 'elemento_pai',
                            typeAhead: true,
                            loadLazy: true,
                            lazyRender: true,
                            editable: false,
                            hiddenValue:(this.values != undefined ? this.values.elemento_pai_id : 0)
                        },
                        {
                            'fieldLabel': 'Enunciado',
                            'xtype': 'textarea',
                            'enableColors': true,
                            'allowBlank': true,
                            'width':'350',
                            'height':'200',
                            'name': 'enunciado'
                        },
                        {
                            'fieldLabel': 'Label',
                            'xtype': 'textfield',
                            'allowBlank': false,
                            'width':'350',
                            'name': 'label'
                        },
                        {
                            'fieldLabel': 'Grupo',
                            'xtype': 'textfield',
                            'allowBlank': false,
                            'width':'350',
                            'name': 'grupo'
                        },
                        {
                            'fieldLabel': 'Mista',
                            'xtype': 'checkbox',
                            'name': 'mista'
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
                'url': toolkit.util.Normalize.controller_action('QQuestao', this.action),
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
                        'title': 'Questão',
                        'msg': message,
                        'icon': Ext.Msg.ERROR,
                        'buttons': Ext.Msg.OK
                    });

                    if(this.callback && this.callback.failure)
                        this.callback.failure.handler.call(this.callback.failure.scope ? this.callback.failure.scope : window);
                },
                'waitMsg': 'Salvando dados da Questão...'
            })
        }
        
    }
);