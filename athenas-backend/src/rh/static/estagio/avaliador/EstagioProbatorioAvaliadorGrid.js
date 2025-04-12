
Ext._define('estagio.avaliador.EstagioProbatorioAvaliadorGrid', {

    extend: 'estagio.gestor.EstagioProbatorioServidorGrid',

    rest: 'estagio.avaliador.EstagioProbatorioAvaliadorRestful',

    configOrderToolBar: ['actionAvaliar', 'actionAlterar', 'openVisualizacao', 'openRelatorio', 'search', '-', '->'],

    hideItemsToolbar: [],

    getActionAvaliarAction: function(cfg) {
        if(!this._actionAvaliar)
            this._actionAvaliar = Ext._create('Ext.Button', {
                text: 'Avaliar',
                iconCls: 'icon-estagio icon-efetivado',
                scope: this,
                handler: this.getAvaliacaoWindow
            });
    
        return this._actionAvaliar;
    },

    getActionAlterarAction: function(cfg) {
        if(!this._actionAlterar)
            this._actionAlterar = Ext._create('Ext.Button', {
                text: 'Alterar Avaliação',
                scope: this,
                iconCls: 'icon-estagio icon-authorization',
                handler: this.getAlteracaoWindow
            });
    
        return this._actionAlterar;
    },

    getAvaliacaoWindow: function(){
        var selected = this.getSelectionModel().getSelected();
        if (selected){
            // var rest = this.factoryRestful();
            var rest = Ext._create('estagio.avaliador.EstagioProbatorioAvaliadorRestful', {});

            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando dados...'});
            mask.show();
            rest.doRequest(
                rest.getRoute('get_list_questionario', [selected.data.questionario_id,selected.data.pk], 'POST', {
                    scope: this,
                    callback: function() {
                        mask.hide();
                        mask = undefined;
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);
                        if(rst.success) {
                            var montaQuestionario = new toolkit.questionario.MontaQuestionario({
                                'title': selected.data.questionario,
                                'action': 'create',
                                'values':rst.collection,
                                'callback': {
                                    'success': {
                                        'scope': this,
                                        'handler': function() { 
                                            Ext.Ajax.request({
                                                url: toolkit.util.Normalize.controller_action('GepEstagioProbatorioAvaliador','save_avaliacao_estagio'),
                                                scope:this,
                                                params:{
                                                    pk_gestor_estagio: selected.data.pk,
                                                    pk_questionario_resposta:montaQuestionario.retorno
                                                },
                                                'success': function(request) {
                                                    var obj = Ext.decode(request.responseText);
                                                    Ext.Msg.show({
                                                        'title': 'Estágio Probatório',
                                                        'icon': Ext.Msg.INFO,
                                                        'buttons': Ext.Msg.OK,
                                                        'msg': obj.message
                                                    });
                                                    this.getStore().reload();
                                                },
                                                failure: function(response, opts) {
                                                    console.log(opts.result.message)
                                                    Ext.Msg.show({
                                                        'title': 'Atenção!',
                                                        'msg': 'Erro ao salvar os dados',
                                                        'icon': Ext.Msg.WARNING,
                                                        'buttons': Ext.Msg.OK
                                                    });
                                                }
                                            });
                                            this.getStore().reload();
                                        }
                                    }
                                }
                            }, rst.collection, selected.data.questionario);

                            montaQuestionario.show();

                            this.getStore().reload();
                        }
                        else
                            Ext.Msg.show({
                                title: 'Atenção',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                    },
                    failure: function(xhr) {
                        console.log('>>> ERRO');
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso indisponível no momento.'
                        });
                    },
                })
            );

        } else {
            Ext.Msg.show({
                title: 'Atenção',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um servidor'
            });
        }

    },

    getAlteracaoWindow: function(){
        var selected = this.getSelectionModel().getSelected();
        if (selected){
            // var rest = this.factoryRestful();
            var rest = Ext._create('estagio.avaliador.EstagioProbatorioAvaliadorRestful', {});

            var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando dados...'});
            mask.show();
            rest.doRequest(
                rest.getRoute('get_questionario_alteracao', [selected.data.questionario_id,selected.data.pk], 'POST', {
                    scope: this,
                    params:{tipo:1},
                    callback: function() {
                        mask.hide();
                        mask = undefined;
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);
                        if(rst.success) {
                            var montaQuestionarioAlteracao = new toolkit.gep.MontaQuestionarioAlteracao({
                                'title': selected.data.questionario,
                                'action': 'update',
                                'values':rst.collection,
                                'callback': {
                                    'success': {
                                        'scope': this,
                                        'handler': function() { 
                                            console.log(montaQuestionarioAlteracao.retorno);
                                            Ext.Ajax.request({
                                                url: toolkit.util.Normalize.controller_action('GepEstagioProbatorioAvaliador','save_alteracao_avaliacao_estagio'),
                                                scope:this,
                                                params:{
                                                    pk_gestor_estagio: selected.data.pk,
                                                    pk_questionario_resposta: montaQuestionarioAlteracao.retorno
                                                },
                                                'success': function(request) {
                                                    var obj = Ext.decode(request.responseText);
                                                    Ext.Msg.show({
                                                        'title': 'Estágio Probatório',
                                                        'icon': Ext.Msg.INFO,
                                                        'buttons': Ext.Msg.OK,
                                                        'msg': obj.message
                                                    });
                                                    this.getStore().reload();
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
                                            this.getStore().reload();
                                        }
                                    }
                                }
                            }, rst.collection, selected.data.questionario);

                            montaQuestionarioAlteracao.show();

                            this.getStore().reload();
                        }
                        else
                            Ext.Msg.show({
                                title: 'Atenção',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                    },
                    failure: function(xhr) {
                        console.log('>>> ERRO');
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso indisponível no momento.'
                        });
                    },
                })
            );

        } else {
            Ext.Msg.show({
                title: 'Atenção',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um servidor'
            });
        }

    },

    getToolbar: function(cfg) {
        var novoComponent;
        if(!this._toolbar) {
            this._toolbar = estagio.avaliador.EstagioProbatorioAvaliadorGrid.superclass.getToolbar.call(this, cfg);
            this._toolbar.findBy(
                function(item) {
                    if(item.text == 'Filtro')
                        novoComponent = item;
                }
            );
            this._toolbar.remove(novoComponent);
        }

        return this._toolbar;
    },

});
