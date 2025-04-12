/**
 *
 * static/siatu/chamado/ManagerGerente.js
 *
 **/

Ext._define('common.siatu.chamado.ManagerGerente', {
    extend: 'toolkit.widget.TabPanel',

    // getter e setter para serviço
    servico: function (value) {
        if (value !== undefined && this._servico !== value) {
            this._servico = value;
            this.observerServico();
        }

        return this._servico;
    },

    observerServico: function () {
        if (this.servico()) {
            this.refreshReport(this.servico());
        } else {
            this.getFormRelatorio().getForm().setValues({'total_chamado': ''});
        }
    },

    rowSelectHandler: function (grid, index, record) {
        this.setChamado(record.get('pk'));
        var servico_atendentes = record.get('servico_atendentes');
        var atendentes = record.get('atendentes');
        this.setServicoAtendentes(servico_atendentes);
        this.setSizeAtendentesChamado(atendentes.length);

        this.observerGridChamados();

        var rest = Ext._create('common.siatu.chamado.Restful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando dados...'});
        mask.show();
        rest.rendererDocument(
            record.get('pk'),
            {
                scope: this,
                fn: function (document) {

                    this.getDetailChamadoTilePagePanel().enable();
                    this.getDetailChamadoTilePagePanel().setPageContent(document.content);
                }
            },
            {
                fn: function (message) {
                    Ext.Msg.show({
                        title: 'Buscando documento',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function () {
                    mask.hide();
                }
            }
        );

        if (record.get('reincidencia') != ''
                && !record.get('reincidencia_confirm_atendente')
                && record.get('status_atual') != 'Concluído') {
            this.getGridChamados().getReincidenciaGerenteButton().enable();
        } else {
            this.getGridChamados().getReincidenciaGerenteButton().disable();
        }

        if (record.get('cancelado') == ''
                && record.get('status_atual') == 'Aberto'
                || record.get('status_atual') == 'Aguardando atendimento') {
            this.getGridChamados().getCancelarButton().enable();
        } else {
            this.getGridChamados().getCancelarButton().disable();
        }

        this.atualizaFormSatisfacao(record);
        this.atualizaFormRelatorio(record);
    },

    rowDeselectHandler: function () {
        this.setChamado(undefined);
        this.observerGridChamados();

        this.getDetailChamadoTilePagePanel().setPageContent('');
        this.getDetailChamadoTilePagePanel().disable();
    },

    getGridChamados: function() {
        if (!this._gridChamados) {
            this._gridChamados = Ext._create('common.siatu.chamado.Grid', {
                region: 'center',
                minHeight: 300,
                split: true,
                manager: 'gerente',
                concluido: this.concluido,
                filterStatus: this.filterStatus,
                filterServico: this.lista_servicos,
                serviceFilterCallback: {
                    scope: this,
                    fn: function(servico) {
                        this.servico(servico);
                    }
                },
                status_callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getTabPrincipal().getStatusGrid().getStore().reload();
                            this._gridChamados.getStore().reload();
                        }
                    }
                },
                cancelar_callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this._gridChamados.getStore().reload();
                            this._gridChamados.getCancelarButton().disable();
                            this.getTabPrincipal().getStatusGrid().getStore().load();
                        }
                    }
                },
                update_callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this._gridChamados.getStore().reload();
                            this.getTabDistribuicaoManual().setStoreAtendenteGrid(this.getChamado());
                        }
                    }
                }
            });

            this._gridChamados.setFilterProperty('servico__in', this.lista_servicos, 0, false);
            this._gridChamados.setFilterProperty('status_atual__status__in', this.filterStatus, 1000, false);

            this._gridChamados.getSelectionModel().on({
                scope: this,
                rowselect: this.rowSelectHandler
            });

            this._gridChamados.getSelectionModel().on({
                scope: this,
                rowdeselect: this.rowDeselectHandler
            });
        }

        return this._gridChamados;
    },

    observerGridChamados: function() {
        if (this.ChamadoId) {
            this.getTabPrincipal().getStatusGrid().setFilterProperty('chamado', this.getChamado());
            this.getTabPrincipal().getStatusGrid().setParam('chamado', this.getChamado());
            this.getTabPrincipal().getListaAtendenteGrid().setFilterProperty('chamados', this.getChamado());

            this.getTabTransferencia().getTransferenciaGrid().setFilterProperty('chamado', this.getChamado());
            this.getTabTransferencia().getTransferenciaGrid().setParam('chamado', this.getChamado());
            this.getTabTransferencia().getTransferenciaGrid().setParam('servico_atendentes', this.getServicoAtendentes());

            if (this.getSizeAtendentesChamado()==0) {
                this.getTabDistribuicaoManual().enable();
                this.getTabDistribuicaoManual().setChamado(this.getChamado());
                this.getTabDistribuicaoManual().getListaAtendenteGrid().setFilterProperty('chamados', this.getChamado());

                this.getTabDistribuicaoManual().setStoreAtendenteGrid(this.getChamado());
            } else {
                this.getTabDistribuicaoManual().disable();
                if(this.getTabs().activeTab.title=='Distribuição Manual')
                    this.getTabPrincipal().show();
            }

            this.getTabTerceiroInterno().setChamado(this.getChamado());
            this.getTabTerceiroInterno().getListaTerceiroGrid().setFilterProperty('chamados', this.getChamado());
            this.getTabTerceiroInterno().setStoreTerceiroGrid(this.getChamado());

            this.getTabAnexo().getGrid().setFilterProperty('chamado', this.getChamado());
            this.getTabAnexo().getGrid().setParam('chamado', this.getChamado());

            this.getTabs().enable();
        } else {
            this.getTabs().disable();
        }
    },

    setChamado: function(pk) {
        this.ChamadoId = pk;
    },

    getChamado: function() {
        return this.ChamadoId;
    },

    setServicoAtendentes: function(atendentes){
        this.ServicoAtendentes = atendentes;
    },

    getServicoAtendentes: function(){
        return this.ServicoAtendentes;
    },

    setSizeAtendentesChamado: function(length) {
        this.SizeAtendentesChamado = length;
    },

    getSizeAtendentesChamado: function() {
        return this.SizeAtendentesChamado;
    },

    getTabPrincipal: function(){
        if (!this._tabPrincipal) {
            this._tabPrincipal = Ext._create('common.siatu.chamado.TabPrincipal', {
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getTabPrincipal().getStatusGrid().getStore().reload();
                            this.getGridChamados().getStore().reload();
                        }
                    }
                }
            });
        }
        return this._tabPrincipal;
    },

    getTabTransferencia: function(){
        if (!this._tabTransferencia) {
            this._tabTransferencia = Ext._create('common.siatu.chamado.TabTransferencia', {
                super_user:true,
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getTabTransferencia().getTransferenciaGrid().getStore().reload();
                            this.getGridChamados().getStore().reload();
                            this.getTabPrincipal().getStatusGrid().getStore().reload();
                            this.getTabPrincipal().getListaAtendenteGrid().getStore().reload();
                        }
                    }
                }
            }
            );
        }
        return this._tabTransferencia;
    },

    getTabDistribuicaoManual: function(){
        if (!this._tabDistribuicao) {
            this._tabDistribuicao = Ext._create('common.siatu.chamado.TabDistribuicaoManual', {
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getTabDistribuicaoManual().setStoreAtendenteGrid(this.getChamado());
                            this.getTabDistribuicaoManual().getListaAtendenteGrid().getStore().reload();
                            this.getGridChamados().getStore().reload();
                            this.getTabPrincipal().getStatusGrid().getStore().reload();
                            this.getTabPrincipal().getListaAtendenteGrid().getStore().reload();
                        }
                    }
                }
            });
        }
        return this._tabDistribuicao;
    },

    getTabTerceiroInterno: function(){
        if (!this._tabTerceiro) {
            this._tabTerceiro = Ext._create('common.siatu.chamado.TabTerceiroInterno', {
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getTabTerceiroInterno().getListaTerceiroGrid().getStore().reload();
                            this.getTabTerceiroInterno().setStoreTerceiroGrid(this.getChamado());
                            this.getGridChamados().getStore().reload();
                            this.getTabPrincipal().getStatusGrid().getStore().reload();
                        }
                    }
                }
            });
        }
        return this._tabTerceiro;
    },

    getTabAnexo: function(){
        if (!this._tabAnexo) {
            this._tabAnexo = Ext._create('common.siatu.chamado.TabAnexo', {});
        }
        return this._tabAnexo;
    },

    atualizaFormRelatorio: function(record) {
        var value = record.get('servico');
        this.servico(value);
    },

    atualizaFormSatisfacao: function(record) {
        store = Ext._create('Ext.data.Store', {
            proxy: Ext._create('Ext.data.HttpProxy', {
                api: {
                    read: core.callAction(
                        "SiatuServico",
                        "action_satisfacao_servico",
                        [
                            record.get('servico'),
                            record.get('pk')
                        ]
                    )
                },
                disableCaching: false,
                defaultHeaders: rest.defaultHeaders,
            }),
            reader: Ext._create('Ext.data.JsonReader', {
                idProperty: 'nome',
                root: 'result',
                totalProperty: 'count',
                successProperty: 'success',
                messageProperty: 'message',
                fields: [
                    {name: 'percentual', type: 'string'},
                    {name: 'maioria', type: 'string'},
                    {name: 'nome', type: 'string'},
                    {name: 'texto', type: 'string'},
                    {name: 'atendentes', type: 'int'},
                    {name: 'chamados_hoje', type: 'string'},
                    {name: 'chamados_abertos', type: 'string'},
                    {name: 'chamados_mes', type: 'string'},
                ]
            }),
            autoLoad: false
        });

        store.load({
            callback: function (record, option, success) {
                this.getFormSatisfacao().getForm().loadRecord(record[0]);
                this.getFormSatisfacaoQtdeChamados().getForm().loadRecord(record[0]);
            },
            scope: this
        });
    },

    getFormSatisfacao: function() {
        if (!this._formSatisfacao) {
            this._formSatisfacao = Ext._create('Ext.form.FormPanel', {
                width: '35%',
                title: 'Satisfação da área',
                items:[
                    {
                        style: 'font-size:13px;',
                        labelStyle: 'font-size:13px;',
                        xtype: 'displayfield',
                        fieldLabel: 'Área avaliada',
                        name: 'nome',
                        hideLabel: true,
                    },
                    {
                        xtype: 'label',
                        style: 'font-size:13px;',
                        text: 'Grau de satisfação da área avaliada:',
                        name: 'label',
                    },
                    Ext._create('Ext.Panel',{
                        labelWidth: 30,
                        border: true,
                        layout: 'form',
                        items:[
                        {
                            xtype: 'displayfield',
                            name: 'maioria',
                        },
                        ]
                    }),
                    {
                        style: 'font-size:13px;',
                        fieldLabel: 'Atendentes Hoje',
                        labelStyle: 'font-size:13px; ',
                        xtype: 'displayfield',
                        name: 'atendentes',
                    },
                ]

            });
        }
        return this._formSatisfacao;
    },

    getFormSatisfacaoQtdeChamados: function() {
        if (!this._formSatisfacaoQtdChamados) {
            this._formSatisfacaoQtdChamados = Ext._create('Ext.form.FormPanel', {
                width: '35%',
                height:300,
                title: 'Chamados',
                items: [
                    {
                        style: 'font-size:13px;',
                        fieldLabel: 'Chamados Abertos Hoje',
                        labelStyle: 'font-size:13px;',
                        xtype: 'displayfield',
                        name: 'chamados_hoje',
                    },
                    {
                        style: 'font-size:13px;',
                        fieldLabel: 'Chamados Abertos no Mês',
                        labelStyle: 'font-size:13px;',
                        xtype: 'displayfield',
                        name: 'chamados_mes',
                    },
                    {
                        style: 'font-size:13px;',
                        fieldLabel: 'Chamados Aguardando Atendimento',
                        labelStyle: 'font-size:13px;',
                        xtype: 'displayfield',
                        name: 'chamados_abertos',
                    },
                    {
                        xtype: 'displayfield',
                        hideLabel: true,
                        name: 'texto',
                        style: 'font-size:13px;',
                        labelStyle: 'font-size:13px;',
                    },
                ]

            });
        }
        return this._formSatisfacaoQtdChamados;
    },

    refreshReport: function(service) {
        var rest = Ext._create('common.siatu.chamado.Restful', {});

        rest.doRequest(
            rest.getRoute('history', false, 'POST', {
                scope: this,
                params: {
                    servico: service,
                },
                callback: function() {
                    // mask.hide();
                    // mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        //this.getFormRelatorio().getForm().findField('total_chamado').setValue(rst.total);
                        this.getFormRelatorio().getForm().setValues({'total_chamado': rst.total});
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

    getFormRelatorio: function() {
        if (!this._formRelatorio) {
            this._formRelatorio = Ext._create('Ext.form.FormPanel', {
                width: '30%',
                title:'Relatório de chamados',
                items:[
                    {
                        style: 'font-size:13px;',
                        fieldLabel: 'Qtde de Chamados nos últimos 6 meses',
                        labelStyle: 'font-size:13px;',
                        xtype: 'displayfield',
                        name: 'total_chamado',
                    },
                ]
            });
        }
        return this._formRelatorio;
    },

    getTabs: function() {
        if (!this._tabPanel) {
            this._tabPanel = Ext._create('Ext.TabPanel', {
                region: 'center',
                minHeight: 200,
                split:true,
                border: true,
                closable: false,
                disabled: true,
                activeTab: 0,
                items: [
                    this.getDetailChamadoTilePagePanel(),
                    this.getTabPrincipal(),
                    this.getTabDistribuicaoManual(),
                    this.getTabTransferencia(),
                    this.getTabTerceiroInterno(),
                    this.getTabAnexo(),
                ]
            });
        }
        return this._tabPanel;
    },

    getGerenciaArea: function() {
        if (!this._gridTeste) {
            this._gridTeste = Ext._create('Ext.Panel', {

                title: 'Gerência da Área',
                region: 'south',
                split: true,
                border: false,
                height: 300,

                collapsible: true,
                // labelWidth: 90,
                autoScroll: true,
                frame: true,

                layout:{
                    type: 'hbox',
                    align: 'strech'
                },

                items: [
                    this.getFormSatisfacao(),
                    this.getFormSatisfacaoQtdeChamados(),
                    this.getFormRelatorio(),
                ]
            });
        }
        return this._gridTeste;
    },

    getDetailChamadoTilePagePanel: function() {
        if (!this._datailProtocolTilePanel) {
            this._datailProtocolTilePanel = Ext._create('core.TilePagePanel', {
                title: 'Resumo',
                disabled: true,
                region: 'center',
                // papperModel: 'card',
                minHeight: 150,
            });
        }
        return this._datailProtocolTilePanel;
    },

    getGridPanel: function() {
        if (!this._gridPanel) {
            this._gridPanel = Ext._create('Ext.Panel', {
                region: 'center',
                width: '55%',
                minWidth: 300,
                split: true,
                border: false,
                layout: 'border',
                items: [
                    this.getGridChamados(),
                    this.getGerenciaArea(),
                ]
            });
        }
        return this._gridPanel;
    },

    getDetailGridPanel: function() {
        if (!this._detailProtocolPanel) {
            this._detailProtocolPanel = Ext._create('Ext.Panel', {
                region: 'east',
                width: '45%',
                split: true,
                border: false,
                layout: 'fit',
                items: [
                    this.getTabs()
                ]
            });
        }
        return this._detailProtocolPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        this.getTabTransferencia().getTransferenciaGrid().setParam('super_user',true);
        this.lista_servicos = cfg.lista_servicos;
        this.lista_todos_servicos = cfg.lista_todos_servicos;
        this.concluido = cfg.concluido;
        this.all_status = cfg.all_status;

        if (Ext.util.Cookies.get('siatu-chamado-filterStatus') != null)
            this.filterStatus = Ext.decode(Ext.util.Cookies.get('siatu-chamado-filterStatus'));
        else
            this.filterStatus = this.all_status;

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Chamados',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGridPanel(),
                    this.getDetailGridPanel(),
                ]
            }
        );

        common.siatu.chamado.ManagerGerente.superclass.constructor.call(this, cfg);
    }
});
