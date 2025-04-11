
if(typeof(toolkit) == "undefiend" || typeof(toolkit.util) == "undefined" || typeof(toolkit.widget)) {

    toolkit.widget.enquete = {}

    toolkit.widget.enquete.Enquete = function(controller) {
        this.controller = controller;
        this.form = {};
        this.panel = {};
        this.combo = {};
        this.radiogroup = {};
        this.radioitems = {};
        this.labelWidth = 125;
        this.defaultsWidth = 350;

    }

    toolkit.widget.enquete.Enquete.prototype = {

        show: function() {
            this.panel = new Ext.Panel({
                title: "Sistema de Enquete",
                closable: true,
                layout: "fit",
                items: [
                    this.createComboQuestionary(),
                   // this.createFormQuestionary()
                ]
            });
            toolkit.Application.tabspace.remove(toolkit.Application.tabspace.getActiveTab());
            toolkit.Application.tabspace.add(this.panel);
            toolkit.Application.tabspace.setActiveTab(this.panel);
            toolkit.Application.tabspace.doLayout();
        },

        createComboQuestionary: function() {

            this.combo = {
                id: "combo",
                fieldLabel: "Questionário",
                xtype: "combo",
                editable: false,
                typeAhead: true,
                triggerAction: 'all',
                displayField:'nome',
                border: false,
                emptyText: 'Selecione um questionário...',
                valueField:'id',
                store: new Ext.data.SimpleStore({
                    fields:['id', 'nome'],
                    data: this.addComboItems()
                }),
                mode:'local'
            };
            this.form["combo"] = new Ext.Panel({
                layout: 'fit',
                style: 'margin: 10pt 0; padding: 0 10pt',
                autoHeight: true,
                border: false,
                items: [this.combo],
                buttons: [
                    {
                        text: 'Selecionar',
                        scope: this,
                        handler: function(){
                            if (this.panel.getComponent('form_questionary') == null) {
                                this.panel.add(this.createFormQuestionary());
                                this.panel.doLayout();
                            }
                            else {
                                if (this.panel.getComponent('form_questionary') != null) {
                                    this.panel.remove('form_questionary');
                                    this.panel.add(this.createFormQuestionary());
                                    this.panel.doLayout();
                                }
                            }
                        }
                    },
                    {
                        text: 'Limpar',
                        scope: this,
                        handler: function(){
                            Ext.getCmp("combo").setValue(null);
                            if (this.panel.getComponent('form_questionary') != null) {
                                this.panel.remove('form_questionary');
                                this.panel.doLayout();
                            }
                            else {
                                Ext.Msg.alert('Atenção', 'Não existe questionário para ser limpo!');
                            }
                        }
                    }
                ]
            });
            return this.form["combo"];
        },

        addComboItems: function() {
            var questionaries = toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                        this.controller,
                        "get_questionaries"
                )
            );
            var quest = [];
            for(var pnt in questionaries) {
                var qq = questionaries[pnt];
                if(typeof(qq) != "function")
                    if (qq.ativo)
                        quest.push(
                            [qq.pk, qq.nome]
                        )
            };
            return quest;
        },

        createFormQuestionary: function() {
            this.form["questionary"] = new Ext.FormPanel({
                id: 'form_questionary',
                autoHeight: true,
                style: 'text-align: left; padding-top: 10px; padding-left: 20px; padding-right: 20px;',
                border: true,
                items: this.createPanelQuestion(),
                buttons: [
                    {
                        text: 'Salvar',
                        scope: this,
                        handler: function(){
                            var votacao = this.form["questionary"].getForm().getValues();
                            console.debug(votacao);

                            var result = toolkit.util.Ajax.request_json(
                                "POST",
                                toolkit.util.Normalize.controller_action(
                                    "ENQUETEVotacao",
                                    "commit",
                                    [Ext.getCmp("combo").getValue()]
                                ),
                                votacao
                            );

                            Ext.getCmp("combo").setValue(null);
                            if (this.panel.getComponent('form_questionary') != null) {
                                this.panel.remove('form_questionary');
                                this.panel.doLayout();
                            }

                            alert(result.message);

                        }
                    }
                ]
            });
            return this.form["questionary"];
        },

        createPanelQuestion: function() {

            var value = 0;
            if (Ext.getCmp("combo").getValue() > 0) {
                value = Ext.getCmp("combo").getValue();
            };
            this.questions = toolkit.util.Ajax.request_json(
                "POST",
                toolkit.util.Normalize.controller_action(
                    this.controller,
                    "get_questions",
                    [value]
                )
            );

            this.qst = [];

            for(var pnt in this.questions) {
                var row = this.questions[pnt];
                if(typeof(this.qst[pnt]) != "function")
                    if (row.ativo)
                        this.qst.push(
                            new Ext.Panel({
                                id: "questao_"+row.pk,
                                layout: "form",
                                title: row.questao,
                                style: "padding: 5px",
                                border: true,
                                bodyBorder: false,
                                collapsed: true,
                                collapsible: true,
                                titleCollapse: true,
                                items: {
                                    items: [
                                        this.createRadioGroupResponse(pnt)
                                    ]
                                }
                        }));
            };
            return this.qst;
        },

        createRadioGroupResponse: function(pnt) {
            this.radiogroup[this.questions[pnt].pk] = new Ext.form.RadioGroup({
                id: 'quest_'+this.questions[pnt].pk,
                columns: 1,
                style: "padding: 3pt",
                items: this.addRadioItems(this.questions[pnt].respostas, this.questions[pnt].pk),
            });
            return this.radiogroup[this.questions[pnt].pk];
        },

        addRadioItems: function(respostas, quest_pk) {

            this.resp = [];
            
            for(var pnt in respostas) {
                var rresp = respostas[pnt];
                if(typeof(rresp) != "function")
                    if (rresp.ativo)
                        this.resp.push(
                                  new Ext.form.Radio({
                                      id: 'resp_'+rresp.pk,
                                      labelSeparator: '',
                                      boxLabel: rresp.resposta,
                                      name: 'quest_'+quest_pk,
                                      inputValue: rresp.pk,
                                  }
                              )
                            )
            };
            return this.resp;
        }

    }
}