

Ext._define('apd.periodicevaluationperformance.ExternalEvaluationWindow', {
    extend: 'Ext.Window',

    getFormPanel: function(cfg) {
        // console.log(cfg.params);
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'hidden',
                        name: 'pk',
                        value: cfg.params.pk
                    },
                    {
                        xtype: 'hidden',
                        name: 'questionario',
                        value: cfg.params.questionario
                    },
                    {
                        xtype: 'hidden',
                        name: 'questionario_id',
                        value: cfg.params.questionario_id
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: "Servidor", 
                        name: 'avaliado',
                        value: cfg.params.avaliado
                    },
                    {
                        fieldLabel: "Avaliador Externo", 
                        name: "external_evaluator", 
                        xtype: "textfield",
                        allowBlank: true,
                        width:450,
                    },
                    {
                        fieldLabel: "Matricula Avaliador Externo", 
                        name: "external_registration", 
                        xtype: "textfield",
                        allowBlank: true,
                        width:450,
                    },
                    {
                        fieldLabel: "Cargo Avaliador Externo", 
                        name: "external_jobposition", 
                        xtype: "textfield",
                        allowBlank: true,
                        width:450,
                    },
                    {
                        fieldLabel: "Lotação Avaliador Externo", 
                        name: "external_workplace", 
                        xtype: "textfield",
                        allowBlank: true,
                        width:450,
                    },
                    {
                        allowBlank: false, 
                        fieldLabel: "Data Avaliação Externa", 
                        name: "date_external_evaluation", 
                        xtype: "datefield",
                        width:450,
                    },
                ]
                    
            });
        return this._formPanel;
    },

    save: function(){
        var form = this.getFormPanel().getForm();
        // console.log(form.getValues());

        var questionario_id = form.getValues().questionario_id;
        var pk = form.getValues().pk;
        var questionario = form.getValues().questionario;
        var external_evaluator = form.getValues().external_evaluator;
        var external_jobposition = form.getValues().external_jobposition;
        var external_workplace = form.getValues().external_workplace;
        var external_registration = form.getValues().external_registration;
        var date_external_evaluation = form.getValues().date_external_evaluation;

        var rest = Ext._create('apd.evaluation.EvaluationRestful', {});

        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando dados...'});
        mask.show();
        rest.doRequest(
            rest.getRoute('get_list_external_questionnaire', [questionario_id, pk], 'POST', {
                scope: this,
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);
                    if(rst.success) {
                        var montaQuestionario = new toolkit.questionario.MontaQuestionario({
                            'title': questionario,
                            'action': 'create',
                            'values':rst.collection,
                            'callback': {
                                'success': {
                                    'scope': this,
                                    'handler': function() { 
                                        Ext.Ajax.request({
                                            url: toolkit.util.Normalize.controller_action('ApdEvaluation','save_external_evaluation'),
                                            scope:this,
                                            params:{
                                                pk_apd: pk,
                                                pk_questionnaire_response: montaQuestionario.retorno,
                                                external_evaluator: external_evaluator,
                                                external_jobposition: external_jobposition,
                                                external_workplace: external_workplace,
                                                external_registration: external_registration,
                                                date_external_evaluation: date_external_evaluation,
                                            
                                            },
                                            'success': function(request) {
                                                var obj = Ext.decode(request.responseText);
                                                Ext.Msg.show({
                                                    'title': 'Estágio Probatório',
                                                    'icon': Ext.Msg.INFO,
                                                    'buttons': Ext.Msg.OK,
                                                    'msg': obj.message
                                                });
                                                this.destroy();
                                            },
                                            failure: function(response, opts) {
                                                // console.log(opts.result.message)
                                                Ext.Msg.show({
                                                    'title': 'Atenção!',
                                                    'msg': 'Erro ao salvar os dados',
                                                    'icon': Ext.Msg.WARNING,
                                                    'buttons': Ext.Msg.OK
                                                });
                                            }
                                        });
                                    }
                                }
                            }
                        }, rst.collection, questionario);

                        montaQuestionario.show();
                    }
                    else{
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                    }
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Atenção',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponível no momento.'
                    });
                },
            })
        );

    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg,
                {
                    title: 'Avaliação Externa',
                    closable: true,
                    height: 400,
                    width: 600
                }
            );

		Ext.apply(
			cfg,
			{
				border: false,
				layout: 'fit',
				items: [
					this.getFormPanel(cfg)
				],
                buttons: [
                    {
                        text: 'Enviar',
                        scope: this,
                        handler: this.save
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]   
			}
		);

		apd.periodicevaluationperformance.ExternalEvaluationWindow.superclass.constructor.call(this, cfg);
    }
});