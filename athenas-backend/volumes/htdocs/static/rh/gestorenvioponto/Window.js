Ext._define('rh.gestorenvioponto.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gestorenvioponto.Restful',

    width: 550,

    constructor: function(cfg) {
        rh.gestorenvioponto.Window.superclass.constructor.call(this, cfg);
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel){
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Matrícula',
                        name: 'matricula',         
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Nome',
                        name: 'nome',         
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Lotação',
                        name: 'lotacao',         
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Categoria Funcional',
                        name: 'categoria_funcional',         
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Aprovador',
                        name: 'aprovador',         
                    },    
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Data Admissão',
                        name: 'dt_admissao',         
                    },                   
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Status',
                        name: 'status',         
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Cód. VDF',
                        name: 'cod_vdf',         
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Teletrabalho',
                        name: 'in_teletrabalho',         
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Afastamento',
                        name: 'tipo_afastamento',         
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Último Envio',
                        name: 'ultimo_envio',         
                    },
                    this.getHistoricoNotificacaoGrid(cfg),
                ],
            });

        }
            
        return this._formPanel;
    },

    getHistoricoNotificacaoGrid: function (cfg) {
        if (!this._historicoNotificacaoGrid)
            this._historicoNotificacaoGrid = new Ext.grid.GridPanel({
                height: 300,
                title:"Histórico de Notificações",
                store: this.getStoreGridHistoricoNotificacao(cfg),
                columns: [
                    { header: 'Data de envio', dataIndex: 'data', width: 150 },
                    { header: 'Email', dataIndex: 'email', width: 250 },
                    { header: 'Usuário', dataIndex: 'usuario', width: 250 },
                ]
            });

        return this._historicoNotificacaoGrid;
    },

    getStoreGridHistoricoNotificacao: function(cfg) {
        if(!this.storeGridHistoricoNotificacao) {
            params = {
                'ano':cfg.values.ano,
                'mes':cfg.values.mes,
                'servidor':cfg.values.pk
            }
            this.storeGridHistoricoNotificacao = new Ext.data.JsonStore({
                fields: [
                    'data',
                    'email',
                    'usuario'
                ],
                root: 'result',
                totalProperty: 'totalRows',
                url: toolkit.util.Normalize.controller_action(
                    'RHGestorEnvioPontos',
                    'get_store_notificacoes',
                    params
                ),
                baseParams: params,
                autoLoad:true
            });
        }
        return this.storeGridHistoricoNotificacao;
    },
});