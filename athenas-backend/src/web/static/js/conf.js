/**
 *
 */

Ext.apply(
    toolkit.web.cms,
    {
        Setup: Ext.extend(
            toolkit.widget.TabPanel,
            {
                commit: function() {
                    var form = this.getFormPanel().getForm();

                    form.waitMsgTarget = this.getEl();

                    form.submit({
                        url: toolkit.util.Normalize.controller_action(
                            'CMSSetup',
                            'commit'
                        ),
                        method: 'POST',
                        waitMsg: 'Salvando as informações de configuração.',
                        success: function(form, action) {

                        },
                        failure: function(form, action) {
                            switch(action.failureType) {
                                case 'connect':
                                    alert('Erro negociando com o servidor, tente novamente mais tarde.');
                                    break;
                                case 'server':
                                    alert(action.result.message);
                                    break;
                                default:
                                    alert('Ocorreu um erro desconhecido. Contacte a equipe de desenvolvimento.');
                                    break;
                            }
                        },
                        scope: this
                    });
                },

                reset: function() {

                },
                getFormPanel: function() {
                    if(!this.formPanel) {
                        this.formPanel = new Ext.form.FormPanel({
                            border: false,
                            items: [
                                {
                                    xtype: 'fieldset',
                                    title: 'Principal',
                                    collapsible: true,
                                    labelWidth: 130,
                                    defaults: {
                                        width: 350
                                    },
                                    items: [
                                        {
                                            xtype: 'textfield',
                                            fieldLabel: 'Endereço',
                                            name: 'frontend',
                                            value: this.values ? this.values.frontend : ''
                                        }
                                    ]
                                },
                                {
                                    xtype: 'fieldset',
                                    title: 'Twitter',
                                    collapsible: true,
                                    layout: 'form',
                                    defaults: {
                                        labelWidth: 120,
                                        defaults: {
                                            width: 350
                                        }
                                    },
                                    items: [
                                        {
                                            xtype: 'fieldset',
                                            title: 'Usuário',
                                            items: [
                                                {
                                                    xtype: 'textfield',
                                                    fieldLabel: 'Username',
                                                    name: 'twitter_user',
                                                    value: this.values ? this.values.twitter_user : ''
                                                },
                                                {
                                                    xtype: 'textfield',
                                                    fieldLabel: 'Token',
                                                    name: 'twitter_user_token',
                                                    value: this.values ? this.values.twitter_user_token : ''
                                                },
                                                {
                                                    xtype: 'textfield',
                                                    fieldLabel: 'Secret Token',
                                                    name: 'twitter_user_token_secret',
                                                    value: this.values ? this.values.twitter_user_token_secret : ''
                                                }
                                            ]
                                        },
                                        {
                                            xtype: 'fieldset',
                                            title: 'Aplicativo',
                                            items: [
                                                {
                                                    xtype: 'textfield',
                                                    fieldLabel: 'App Name',
                                                    name: 'twitter_app',
                                                    value: this.values ? this.values.twitter_app : ''
                                                },
                                                {
                                                    xtype: 'textfield',
                                                    fieldLabel: 'Consumer Key',
                                                    name: 'twitter_app_token',
                                                    value: this.values ? this.values.twitter_app_token : ''
                                                },
                                                {
                                                    xtype: 'textfield',
                                                    fieldLabel: 'Consumer Secret',
                                                    name: 'twitter_app_token_secret',
                                                    value: this.values ? this.values.twitter_app_token_secret : ''
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    xtype: 'fieldset',
                                    title: 'BitLy shorten',
                                    collapsible: true,
                                    labelWidth: 130,
                                    defaults: {
                                        width: 350
                                    },
                                    items: [
                                        {
                                            xtype: 'textfield',
                                            fieldLabel: 'User',
                                            name: 'bitly_user',
                                            value: this.values ? this.values.bitly_user : ''
                                        },
                                        {
                                            xtype: 'textfield',
                                            fieldLabel: 'Token',
                                            name: 'bitly_token',
                                            value: this.values ? this.values.bitly_token : ''
                                        }
                                    ]
                                }
                            ]
                        })
                    }

                    return this.formPanel;
                },

                constructor: function() {
                    var cf = {
                        title: 'Rede Social',
                        closable: true,
                        items: [
                            {
                                border: false,
                                xtype: 'panel',
                                html: '<div class="loading"><p>Carregando informações de configuração.</p></div>'
                            }
                        ],
                        style: 'padding: 10pt',
                        buttonAlign: 'center',
                        buttons: [
                            {
                                text: 'Salvar',
                                handler: this.commit,
                                scope: this
                            },
                            {
                                text: 'Restaurar',
                                handler: this.reset,
                                scope: this
                            }
                        ]
                    };

                    toolkit.web.cms.Setup.superclass.constructor.call(this, cf);

                    // var ts = toolkit.Application.tabspace;

                    // ts.remove(ts.getActiveTab());
                    // ts.add(this);
                    // ts.setActiveTab(this);

                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action('CMSSetup', 'load'),
                        success: function(request) {
                            this.values = Ext.decode(request.responseText);

                            this.removeAll();
                            this.add(this.getFormPanel());
                            this.doLayout();
                        },
                        scope: this
                    })
                }
            }
        )
    }
);

