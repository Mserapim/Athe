

Ext._define('estagio.avaliador.EstagioProbatorioAvaliadorExternoWindow', {
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
                        name: "avaliador_externo", 
                        xtype: "textfield",
                        allowBlank: true,
                        width:450,
                    },
                    {
                        fieldLabel: "Matricula Avaliador Externo", 
                        name: "matricula_externo", 
                        xtype: "textfield",
                        allowBlank: true,
                        width:450,
                    },
                    {
                        fieldLabel: "Cargo Avaliador Externo", 
                        name: "cargo_externo", 
                        xtype: "textfield",
                        allowBlank: true,
                        width:450,
                    },
                    {
                        fieldLabel: "Lotação Avaliador Externo", 
                        name: "lotacao_externo", 
                        xtype: "textfield",
                        allowBlank: true,
                        width:450,
                    },
                    {
                        allowBlank: false, 
                        fieldLabel: "Data Avaliação Externa", 
                        name: "data_avaliacao_externa", 
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
        var avaliador_externo = form.getValues().avaliador_externo;
        var cargo_externo = form.getValues().cargo_externo;
        var lotacao_externo = form.getValues().lotacao_externo;
        var matricula_externo = form.getValues().matricula_externo;
        var data_avaliacao_externa = form.getValues().data_avaliacao_externa;

        var rest = Ext._create('estagio.avaliador.EstagioProbatorioAvaliadorRestful', {});

        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando dados...'});
        mask.show();
        rest.doRequest(
            rest.getRoute('get_list_questionario_externo', [questionario_id, pk], 'POST', {
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
                                            url: toolkit.util.Normalize.controller_action('GepEstagioProbatorioAvaliador','save_avaliacao_estagio_externo'),
                                            scope:this,
                                            params:{
                                                pk_gestor_estagio: pk,
                                                pk_questionario_resposta: montaQuestionario.retorno,
                                                avaliador_externo: avaliador_externo,
                                                cargo_externo: cargo_externo,
                                                lotacao_externo: lotacao_externo,
                                                matricula_externo: matricula_externo,
                                                data_avaliacao_externa: data_avaliacao_externa,
                                            
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

		estagio.avaliador.EstagioProbatorioAvaliadorExternoWindow.superclass.constructor.call(this, cfg);
    }
});