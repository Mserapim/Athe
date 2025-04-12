
if(typeof(toolkit) == "undefiend" || typeof(toolkit.util) == "undefined" || typeof(toolkit.widget)) {

    toolkit.widget.auth = {}

    toolkit.widget.auth.Profile = function(user_id) {
        this.user_id = user_id;
        this.form = {};
        this.labelWidth = 125;
        this.defaultsWidth = 350;
    }

    toolkit.widget.auth.Profile.prototype = {

        show: function() {
            this.panel = new Ext.Panel({
                title: "Perfil do Usuário",
                closable: true,
                layout: "fit",
                items: [
                    new Ext.TabPanel({
                        activeTab: 0,
                        tabPosition: "bottom",
                        border: false,
                        items: [
                            {
                                title: "Informações Pessoais",
                                layout: "fit",
                                items: [
                                    new Ext.Panel({
                                        layout: "fit",
                                        style: "padding: 15pt",
                                        border: false,
                                        items: [this.createFormPanelInformation()]
                                    })
                                ]
                            },
                            {
                                title: "Credenciais de acesso",
                                layout: "fit",
                                items: [
                                    new Ext.Panel({
                                        layout: "fit",
                                        style: "padding: 15pt",
                                        border: false,
                                        items: [this.createFormPanelPassword()]
                                    })
                                ]
                            },
                           {
                               title: "Preferências",
                               layout: "fit",
                               items: [
                                   new Ext.Panel({
                                       layout: "fit",
                                       style: "padding: 15pt",
                                       border: false,
                                       items: [this.createFormPanelPreference()]
                                   })
                               ]
                           }
                        ]
                    })
                ]
            });

            toolkit.Application.tabspace.remove(toolkit.Application.tabspace.getActiveTab());
            toolkit.Application.tabspace.add(this.panel);
            toolkit.Application.tabspace.setActiveTab(this.panel);

            toolkit.Application.tabspace.doLayout();
        },

        getUserInformation: function() {
            return toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    "AUTHProfile",
                    "get_user_information"
                ),
                {
                    "user_id": this.user_id
                }
            );
        },

        createFormPanelInformation: function() {

            var info = this.getUserInformation();

            this.form["information"] = new Ext.FormPanel({
                border: false,
                defaults: {
                    width: this.defaultsWidth,
                    labelStyle: "text-align:right"
                },
                labelWidth: this.labelWidth,
                items: [
                    {
                        fieldLabel: "Primeiro nome",
                        xtype: "textfield",
                        name: "first_name",
                        value: info.first_name
                    },
                    {
                        fieldLabel: "Sobrenome",
                        xtype: "textfield",
                        name: "last_name",
                        value: info.last_name
                    },
                   // {
                   //     fieldLabel: "Telefone",
                   //     xtype: "fonefield",
                   //     name: "fone_res"
                   // },
                   // {
                   //     fieldLabel: "Telefone celular",
                   //     xtype: "fonefield",
                   //     name: "fone_cel"
                   // },
                   // {
                   //     fieldLabel: "Fax",
                   //     xtype: "fonefield",
                   //     name: "fone_fax"
                   // },
                    {
                        fieldLabel: "E-mail",
                        xtype: "textfield",
                        name: "email",
                        value: info.email
                    },
                    {
                        fieldLabel: "Senha",
                        xtype: "textfield",
                        inputType: "password",
                        name: "credencial"
                    }
                ],
                buttonAlign: "center",
                buttons: [
                    {
                        text: "Salvar",
                        handler: function() {
                            var url = toolkit.util.Normalize.controller_action("AUTHProfile", "change_user_information");
                            var values = this.form["information"].getForm().getValues();

                            var obj = toolkit.util.Ajax.request_json(
                                "POST",
                                url,
                                values
                            )

                            if(!obj.status) {
                                alert(obj.message);
                            }
                            else {
                                alert("Dados alterados com sucesso.");
                            }

                            this.form["information"].getComponent(3).setValue("");

                        },
                        scope: this
                    },
                    {
                        text: "Resetar",
                        handler: function() {
                            this.form["information"].getForm().reset();
                        },
                        scope: this
                    },
                ]
            });

            return this.form["information"];
        },

        createFormPanelPreference: function() {
            this.form["preference"] = new Ext.FormPanel({
                border: false,
                defaults: {
                    width: this.defaultsWidth,
                    labelStyle: "text-align:right"
                },
                labelWidth: this.labelWidth,
                items: [
                ],
                buttonAlign: "center",
                buttons: [
                    {
                        text: "Salvar"
                    },
                    {
                        text: "Resetar"
                    },
                ]
            });

            return this.form["preference"];
        },

        createFormPanelPassword: function() {
            this.form["password"] = new Ext.FormPanel({
                border: false,
                defaults: {
                    width: this.defaultsWidth,
                    labelStyle: "text-align:right"
                },
                labelWidth: this.labelWidth,
                items: [
                    {
                        fieldLabel: "Senha antiga",
                        xtype: "textfield",
                        inputType: "password",
                        name: "senha_antiga",
                        allowBlank: false
                    },
                    {
                        fieldLabel: "Nova senha",
                        xtype: "textfield",
                        inputType: "password",
                        name: "senha_nova",
                        allowBlank: false
                    },
                    {
                        fieldLabel: "Confirmar senha",
                        xtype: "textfield",
                        inputType: "password",
                        name: "senha_confirma",
                        allowBlank: false
                    }
                ],
                buttonAlign: "center",
                buttons: [
                    {
                        text: "Salvar",
                        handler: function() {
                            var values = this.form["password"].getForm().getValues();

                            values["user_id"] = this.user_id.toString();

                            var result = toolkit.util.Ajax.request_json(
                                "POST",
                                toolkit.util.Normalize.controller_action(
                                    "AUTHProfile",
                                    "change_password"
                                ),
                                values
                            );

                            alert(result.message);
                            if(result.result)
                                this.form["password"].getForm().reset();
                        },
                        scope: this
                    },
                    {
                        text: "Resetar",
                        handler: function() {
                            this.form["password"].getForm().reset();
                        },
                        scope: this
                    }
                ]
            });

            return this.form["password"];
        }

    }

}
