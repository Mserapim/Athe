
if(typeof(toolkit) == "undefiend" || typeof(toolkit.util) == "undefined" || typeof(toolkit.widget)) {

    toolkit.widget.enquete.graph = {}

    toolkit.widget.enquete.Graph = function(controller) {
        this.controller = controller;
        this.form = [];
        this.questions = [];
        this.data = [];
        this.data2 = [];
        this.answers = [];
        this.store = new Ext.data.JsonStore({});
        this.combo = {};
        this.labelWidth = 125;
        this.defaultsWidth = 350;

    }

    toolkit.widget.enquete.Graph.prototype = {

        show: function() {
            this.panel = new Ext.Panel({
                title: "Sistema de Enquete",
                closable: true,
                layout: "fit",
                items: [
                    this.createComboQuestionary(),
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
                            if (this.panel.getComponent('graph_questionary') == null) {
                                this.panel.add(this.createFormGraph());
                                this.panel.doLayout();
                            }
                            else {
                                if (this.panel.getComponent('graph_questionary') != null) {
                                    this.panel.remove('graph_questionary');
                                    this.panel.add(this.createFormGraph());
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
                            if (this.panel.getComponent('graph_questionary') != null) {
                                this.panel.remove('graph_questionary');
                                this.panel.doLayout();
                            }
                            else {
                                Ext.Msg.alert('Atenção', 'Não existe gráfico para ser limpo!');
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

        createFormGraph: function() {

            this.store = new Ext.data.JsonStore({
                fields: ['q','quest', 'r1', 't1', 'r2', 't2', 'r3', 't3', 'r4', 't4', 'r5', 't5'],
                data: this.getDataGraph()
            });

            this.form["graph"] = new Ext.Panel({
                id: "graph_questionary",
                style: 'margin: 10pt 0; padding: 0 10pt',
                height: 400,
                renderTo: document.body,
                items: {
                        xtype: 'barchart',
                        store: this.store,
                        yField: 'q',
                        tipRenderer : function(chart, record, index, series){
                            if(series.xField == 'r1'){
                                return record.data.quest + '\nResposta: ' + record.data.t1 + '\nVotos: ' + record.data.r1;
                            };
                            if(series.xField == 'r2'){
                                return record.data.quest + '\nResposta: ' + record.data.t2 + '\nVotos: ' + record.data.r2;
                            };
                            if(series.xField == 'r3'){
                                return record.data.quest + '\nResposta: ' + record.data.t3 + '\nVotos: ' + record.data.r3;
                            };
                            if(series.xField == 'r4'){
                                return record.data.quest + '\nResposta: ' + record.data.t4 + '\nVotos: ' + record.data.r4;
                            };
                            if(series.xField == 'r5'){
                                return record.data.quest + '\nResposta: ' + record.data.t5 + '\nVotos: ' + record.data.r5;
                            };
                        },
                        series: [{
                            xField: 'r1',
                        },{
                            xField: 'r2'
                        },{
                            xField: 'r3'
                        },{
                            xField: 'r4'
                        },{
                            xField: 'r5'
                        }],
                    extraStyle: {
                        xAxis: {
                            labelRotation: -90
                        }
                    }
                }
            });
            return this.form["graph"];
        },

        getDataGraph: function() {

            this.questions = [];
            this.data = [];

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
            for(var pnt in this.questions) {
                var row = this.questions[pnt];
                if(typeof(this.data[pnt]) != "function") {
                    var qst = {};
                    qst = {q: 'Q'+row.pk,quest: row.questao};
                    this.answers = toolkit.util.Ajax.request_json(
                        "POST",
                        toolkit.util.Normalize.controller_action(
                            this.controller,
                            "get_answers",
                            [row.pk]
                        )
                    );
                    var i = 1;
                    for (var pnt2 in this.answers) {
                        var row2 = this.answers[pnt2];
                        if(typeof(this.data2[pnt2]) != "function") {
                            qst['r'+i] = row2.count;
                            qst['t'+i] = row2.resposta;
                            i++;
                        }
                    }

                    this.data.push(qst);
                }
            };
            return this.data;

        },

        getLabel: function(idx){
            var rec = this.store.getAt(idx);
            return rec.get('t1');
        }


    }
}