

Ext._define('apd.periodicevaluationperformance.RepeatLastManualEvaluationWindow', {
    extend: 'Ext.Window',

    getFormPanel: function(cfg) {
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
                        xtype: "rest-autocompletefield",
                        width: 450,
                        fieldLabel: "Avaliador",
                        allowBlank: false,
                        rest: "rh.employee.Restful",
                        name: "evaluator",
                    },
                    {
                        xtype: 'ckeditor',
                        fieldLabel: 'Justificativa',
                        height: 300,
                        name: 'text_justification_repetition'
                    }
                ]
                    
            });
        return this._formPanel;
    },

    save: function(){
        var form = this.getFormPanel().getForm();
        var questionario_id = form.getValues().questionario_id;
        var pk = form.getValues().pk;
        var questionario = form.getValues().questionario;
        var evaluator = form.getValues().evaluator;
        var rest = Ext._create('apd.evaluation.EvaluationRestful', {});
        var text_justification_repetition = form.getValues().text_justification_repetition;
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
                                            url: toolkit.util.Normalize.controller_action('ApdEvaluation','save_evaluation'),
                                            scope:this,
                                            params:{
                                                pk_apd: pk,
                                                pk_questionnaire_response: montaQuestionario.retorno,
                                                evaluator: evaluator,
                                                manual: 'True',
                                                text_justification_repetition: text_justification_repetition,
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
                title: 'Repetir Última Avaliação Manual',
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

		apd.periodicevaluationperformance.RepeatLastManualEvaluationWindow.superclass.constructor.call(this, cfg);
    }
});