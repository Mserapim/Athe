Ext._define('corregedoria.cirdir.health.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.cirdir.health.Window',

    configOrderToolBar: ['add', 'edit', 'remove','-', 'history', '-', 'confirmRecommendation', '->','submit', ],

    getFilterHealthAction: function() {
        if(!this._filterHealthAction){
            this._filterHealthAction = new Ext.Button({
                xtype: 'button',
                text: 'Exibir',
                iconCls: 'icon-crgmpe icon-crgmpe-find',
                menu: [
                    {
                        text: 'Aguardando distribuição',
                        iconCls: 'icon-crgmpe icon-crgmpe-health',
                        scope: this,
                        handler: function() { this.getNoDelivered(); }
                    },
                    {
                      text: 'Distribuídos',
                      iconCls: 'icon-crgmpe icon-crgmpe-list',
                      scope: this,
                      handler: function() { this.getDelivered(); }
                    },
                    {
                        text: 'Avaliações pendentes',
                        iconCls: 'icon-crgmpe icon-crgmpe-waiting',
                        scope: this,
                        handler: function() { this.getNoEvaluated(); }
                    },
                    {
                      text: 'Avaliados',
                      iconCls: 'icon-crgmpe icon-crgmpe-success',
                      scope: this,
                      handler: function() { this.getEvaluated(); }
                    },
                    '-',
                    {
                        text: 'Mostrar Todos',
                        iconCls: 'icon-crgmpe icon-crgmpe-list-papers',
                        scope: this,
                        handler: function() { this.showAllAssessment(true); }
                    },
                ]
            });
        }
        return this._filterHealthAction;
    },

    getConfirmRecommendationAction: function(cfg) {
        if(!this._confirmRecommendationAction) {

            this._confirmRecommendationAction = Ext._create('Ext.Button', {
                text: 'Ciência da recomendação',
                iconCls: 'icon-crgmpe icon-crgmpe-autorizado',
                disabled: cfg.params.closed_health,
                scope: this,
                handler: function() {
                    this._confirmeRecommendation();
                }
            });
        }
        return this._confirmRecommendationAction;
    },

    _confirmeRecommendation: function() {
        var selected = this.getSelectionModel().getSelected();
        if(selected) {
            console.log(selected);
            Ext.Ajax.request({
                scope: this,
                method: 'POST',
                params: {
                    health: selected.get('pk')
                },
                url: core.callAction('CIRDIRHealthAssessmentRestful', 'confirm_recommendation'),
                callback: function() {
                    core.invokeCallback((this.callback || {}).success);
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);
                    if (rst.success) {
                        Ext.Msg.show({
                            title: 'Ciência da recomendação',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    } else {
                        Ext.Msg.show({
                            title: 'Ciência da recomendação',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                failure: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Ciência da recomendação',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
            });
        } else {
            Ext.Msg.show({
                title: 'Confirmar leitura da recomendação',
                msg: 'Selecione o questionário que possua a recomendação que deseja confirmar.',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK
            });
        }
    },

    getYearStore: function() {
        if(!this._yearStore)
            this._yearStore = new Ext.data.Store({
                proxy: new Ext.data.HttpProxy({
                    url: toolkit.util.Normalize.controller_action('CIRDIRControlInformation', 'years'),
                    method: 'GET',
                    disableCaching: false
                }),
                reader: new Ext.data.JsonReader({
                    root: 'collection',
                    totalProperty: 'count',
                    fields: [
                        {name: 'year', type: 'int'}
                    ]
                })
            });

        return this._yearStore;
    },

    getYearFieldAction: function(cfg) {
        if(!this._yearField) {
            this._yearField = Ext._create('core.fields.ComboField', {
                displayField: 'year',
                valueField: 'year',
                store: this.getYearStore(),
                hiddenName: 'year',
                allowBlank: false,
                width: 80,
            });
            this._yearField.on({
                scope: this,
                select: function(cmb, record, index, valid) {
                    if(valid) {
                        this.fireEvent('yearselected', record.get('year'));
                    }
                }
            });

        }
        return this._yearField;
    },

    getEvaluated: function() {
        this.showAllAssessment(false);
        this.addFilterProperty('health_assessments__signed_by__isnull', false, 100, false);
        this.addFilterProperty('health_assessments__isnull', false, 101, true);
    },

    getNoEvaluated: function() {
        this.showAllAssessment(false);
        this.addFilterProperty('health_assessments__signed_by__isnull', true, 100, false);
        this.addFilterProperty('health_assessments__isnull', false, 101, true);
    },

    getDelivered: function() {
      this.showAllAssessment(false);
      this.addFilterProperty('health_assessments__isnull', false, 101, true);
    },

    getNoDelivered: function() {
        this.showAllAssessment(false);
        this.addFilterProperty('health_assessments__isnull', true, 101, true);
    },

    showAllAssessment: function(reload) {
        this.removeFilterProperty('health_assessments__signed_by__isnull', 100, false);
        this.removeFilterProperty('health_assessments__isnull', 101, reload);
    },

    getHistoryAction: function(cfg) {
        if(!this._historyAction){
            this._historyAction = new Ext.Button({
                xtype: 'button',
                text: 'Histórico',
                iconCls: 'icon-crgmpe icon-crgmpe-list',
                handler: function() {
                    Ext._create('corregedoria.cirdir.HistoryWindow', {
                        params: {
                          controlinformation: cfg.params.controlinformation,
                          criteria_key: 5,
                        },
                    }).show();
                }
            });
        }
        return this._historyAction;
    },

    getSubmitAction: function(cfg) {
        if(!this._submitAction){
            this._submitAction = new Ext.Button({
                xtype: 'button',
                text: 'Submeter Saúde',
                iconCls: 'icon-crgmpe icon-crgmpe-success',
                disabled: cfg.params.closed_health,
                handler: function() {
                  Ext.Msg.show({
                      title: 'Submeter a Saúde',
                      msg: 'Tem certeza que deseja submeter as informações de Saúde?',
                      icon: Ext.Msg.QUESTION,
                      buttons: Ext.Msg.YESNO,
                      scope: this,
                      fn: function(btn_submit) {
                          if(btn_submit=='no') return;
                          Ext.Msg.show({
                              title: 'Submeter Saúde',
                              msg: 'Deseja incluir as informações de saúde no Projeto <b>Você é Único</b>, para diagnóstico e acompanhamento junto a Área de Saúde?',
                              icon: Ext.Msg.QUESTION,
                              buttons: Ext.Msg.YESNO,
                              scope: this,
                              fn: function(btn_authorization) {
                                Ext.Ajax.request({
                                    scope: this,
                                    url: core.callAction('CIRDIRControlInformation', 'submit'),
                                    callback: function() {
                                        cfg.params.mainGrid.getStore().reload();
                                    },
                                    success: function(request) {
                                        var rst = Ext.decode(request.responseText);
                                        if (rst.success == true) {
                                            Ext.Msg.show({
                                                title: 'Submeter Saúde',
                                                msg: rst.message,
                                                icon: Ext.Msg.INFO,
                                                buttons: Ext.Msg.OK
                                            });
                                        } else {
                                            Ext.Msg.show({
                                                title: 'Submeter Saúde',
                                                msg: rst.message,
                                                icon: Ext.Msg.ERROR,
                                                buttons: Ext.Msg.OK
                                            });
                                        }
                                        core.invokeCallback((this.callback || {}).success);
                                    },
                                    failure: function(request) {
                                        var rst = Ext.decode(request.responseText);
                                        Ext.Msg.show({
                                            title: 'Submeter Saúde',
                                            msg: rst.message,
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        });
                                    },
                                    params: {
                                        controlinformation: cfg.params.controlinformation,
                                        criteria: 'health',
                                        authorization_health: btn_authorization == 'yes' ? true : false,
                                    },
                                });
                              }
                          });
                      }
                  });
                }
            });
        }
        return this._submitAction;
    },

    delete: function(record, cfg) {
        if (record.authorization_health == true) {
            Ext.Msg.show({
                title: 'Removendo',
                msg: 'Remoção não permitida. Informação importada do sistema SRDIR.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        } else {
            Ext.Msg.show({
                title: 'Alerta',
                msg: 'Confirma a exclusão do item selecionado?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn_submit) {
                    if(btn_submit=='no') return;
                    health_area = cfg.params.health_area;
                    var mask = new Ext.LoadMask(this.getEl(), {msg: 'Removendo item...'});
                    mask.show();
                    Ext.Ajax.request({
                        scope: this,
                        url: core.callAction('CIRDIRHealth', 'delete'),
                        callback: function() {
                            this.getStore().reload();
                            mask.hide();
                        },
                        success: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Removendo',
                                msg: rst.message,
                                icon: rst.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        failure: function(request) {
                            var rst = Ext.decode(request.responseText);
                            Ext.Msg.show({
                                title: 'Removendo',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        params: {
                            'health_pk': record.id,
                            'health_area': health_area,
                        }
                    });
                }
            });
        }
    },

    removeItems: function(record, cfg) {
        var selected = this.getSelectionModel().getSelected();
        if (selected) {
            this.delete(selected, this);
        } else {
            Ext.Msg.show({
                title: 'Removendo',
                msg: 'Não foi selecionado nenhum item para remoção.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getColumnModel: function(cfg) {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 100, renderer: core.rendererIconGrid},
                    {header: 'Data/Hora de Criação', dataIndex: 'unicode', id: 'autoExpandColumn', hidden: ((cfg.hiddenColumns) || {}).health},
                    {header: 'Membro', dataIndex: 'integrant_unicode', width: 250, hidden: ((cfg.hiddenColumns) || {}).employee},
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.health.Restful',
    'corregedoria.cirdir.health.Grid'
);
