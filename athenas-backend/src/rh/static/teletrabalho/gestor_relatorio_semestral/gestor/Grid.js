/**
 *
 **/
Ext._define('rh.teletrabalho.gestor_relatorio_semestral.gestor.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.teletrabalho.gestor_relatorio_semestral.gestor.Window',

    keywordFieldMessage: 'Palavra-chave',

    hideItemsToolbar: ['add', 'edit', 'remove'],

    hideActions: ['add', 'edit', 'remove', 'copy'],

    configOrderToolBar: ['-', 'search', '->'],

    constructor: function (cfg) {
        //cfg = core.nullValue(cfg, {});
        this.listaPeriodos = cfg.lista_periodos;

        rh.teletrabalho.gestor_relatorio_semestral.gestor.Grid.superclass.constructor.call(this, cfg);

        this.setParam('data_inicio', this.converterDataFormato(this.listaPeriodos[0].data_inicio_analisado));
        this.setParam('data_fim', this.converterDataFormato(this.listaPeriodos[0].data_fim_analisado));
        this.setParam('periodo_pk', this.listaPeriodos[0].id);
        this.getStore().baseParams['periodo_pk'] = this.listaPeriodos[0].id;


        this.setFilterProperty('aprovador_teletrabalho__data_inicio__lte', this.converterDataFormato(this.listaPeriodos[0].data_fim_analisado), 1, false);
        this.setFilterProperty('aprovador_teletrabalho__data_fim__gte' ,this.converterDataFormato(this.listaPeriodos[0].data_inicio_analisado), 2, true);
        
        
    },

    periodosMenuItems: function() {
        var _periodosMenuItems = []
        var that = this;
        this.listaPeriodos.forEach(function(itemPeriodo, index){
            _periodosMenuItems.push({
                id: "periodoId_"+itemPeriodo.id,
                text: itemPeriodo.label,
                checked: index === 0, //false,
                scope: this,
                hideOnClick: false,
                groupMenu: 'grupo_periodo',
                handler: function(chk) { that.filtrarPeriodo(chk, itemPeriodo) },
            });
        });
        return _periodosMenuItems;
    },


    getPeriodoMenuItemsAtualizado:function(){
        let periodosItens = null;
        this._toolbar.items.items.forEach(function(item){
            if(item.text == 'Filtros'){
                item.menu.items.items.forEach(function(itemMenu){
                if(itemMenu.name == 'periodo'){
                    periodosItens = itemMenu.menu.items.items;
                }
            });
        }
        });
        return periodosItens
    },


    getFiltroMenu: function () {
        return [
            {
                name: 'periodo',
                groupMenu: '',
                text: 'Periodo',
                scope: this,
                menu: this.periodosMenuItems()
            },
            {
                name: 'situacao',
                groupMenu: '',
                text: 'Situação',
                scope: this,
                menu: this.situacaoMenuItems()
            },
           
        ]
    },


    situacaoMenuItems: function() {
        var _situacaoMenuItems = [
            {
                id: 'TodasSituacao',
                text: 'Todos',
                checked: true,
                scope: this,
                hideOnClick: false,
                groupMenu: 'grupo_situacaao',
                handler: function(chk) {this.filtrarSituacao(chk, 'TodasSituacao')},
            },
            {
                id: 'EnviadosSituacoes',
                text: 'Enviados',
                checked: false,
                scope: this,
                hideOnClick: false,
                groupMenu: 'grupo_situacaao',
                handler: function(chk) {this.filtrarSituacao(chk, 'EnviadosSituacoes')},
            },
            {
                id: 'NaoEnviadoSituacao',
                text: 'Não Enviados',
                checked: false,
                scope: this,
                hideOnClick: false,
                groupMenu: 'grupo_situacaao',
                handler: function(chk) {this.filtrarSituacao(chk, 'NaoEnviadoSituacao')},
            },
        ];
        
        return _situacaoMenuItems;
    },


    filtrarSituacao: function(chk, opcaoId) {
        var situacaoItens = null;
        this._toolbar.items.items.forEach(function(item){
            if(item.text == 'Filtros'){
                item.menu.items.items.forEach(function(itemMenu){
                    if(itemMenu.name == 'situacao'){
                        situacaoItens = itemMenu.menu.items.items;
                    }
                });
            }
        });

    
        if(opcaoId == 'TodasSituacao' && !chk.checked == true){
            situacaoItens.forEach(function(itemMenuSituacao){
                if(itemMenuSituacao.text != 'TodasSituacao'){ itemMenuSituacao.setChecked(false); }
            });

            this.getStore().baseParams['situacao'] = 'todos';
            this.getStore().load();

        } else if(opcaoId == 'EnviadosSituacoes' && !chk.checked == true){
            situacaoItens.forEach(function(itemMenuSituacao){
                if(itemMenuSituacao.text != 'EnviadosSituacoes'){ itemMenuSituacao.setChecked(false); }
            });

            //this.setFilterProperty('portal_request_employee__relatoriosemestralteletrabalho__isnull', false, 1, true);



            this.getStore().baseParams['situacao'] = 'enviado';
            this.getStore().load();


        } else if(opcaoId == 'NaoEnviadoSituacao' && !chk.checked == true){
            situacaoItens.forEach(function(itemMenuSituacao){
                if(itemMenuSituacao.text != 'NaoEnviadoSituacao'){ itemMenuSituacao.setChecked(false); }
            });

            this.getStore().baseParams['situacao'] = 'naoEnviado';
            this.getStore().load();

        }
    
    },




    filtrarPeriodo: function (chk, opcao) {
        var that = this
        this.removeFilterProperty('aprovador_teletrabalho__data_inicio__lte', 1, false);
        this.removeFilterProperty('aprovador_teletrabalho__data_fim__gte', 2, false);

        let periodosItens = this.getPeriodoMenuItemsAtualizado();

        if (!chk.checked){

            periodosItens.forEach(function(itemPeriodo){
                var periodo_id = itemPeriodo.id.split('_')[1];
                if(periodo_id == opcao.id){
                    data_inicio = that.converterDataFormato(opcao.data_inicio_analisado);
                    data_fim = that.converterDataFormato(opcao.data_fim_analisado);
                    that.setParam('periodo_pk', periodo_id);
                    that.getStore().baseParams['periodo_pk'] = periodo_id;



                }
                else{
                    itemPeriodo.setChecked(false);
                }
            })
            
            if(data_inicio != null && data_fim != null){
                this.setFilterProperty('aprovador_teletrabalho__data_inicio__lte',data_fim, 1, false);
                this.setFilterProperty('aprovador_teletrabalho__data_fim__gte' ,data_inicio, 2, true);
                
                that.setParam('data_inicio', data_inicio);
                that.setParam('data_fim', data_fim);
            }
        }else{
            periodosItens[0].setChecked(true);
            this.setFilterProperty('aprovador_teletrabalho__data_inicio__lte', this.converterDataFormato(this.listaPeriodos[0].data_fim_analisado), 1, false);
            this.setFilterProperty('aprovador_teletrabalho__data_fim__gte' ,this.converterDataFormato(this.listaPeriodos[0].data_inicio_analisado), 2, true);
            
            that.setParam('data_inicio', this.converterDataFormato(this.listaPeriodos[0].data_inicio_analisado));
            that.setParam('data_fim', this.converterDataFormato(this.listaPeriodos[0].data_fim_analisado));
            that.setParam('periodo_pk', this.listaPeriodos[0].id);
            that.getStore().baseParams['periodo_pk'] = this.listaPeriodos[0].id;


        }

        //this.atualizaAnotacaoGrid();

    },


    atualizaAnotacaoGrid: function() {
        var store = this.getStore();
        store.load({});
    },

   
    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Chave', dataIndex: 'pk', width: 55, hidden: true , id: 'autoExpandColumn' },
                    { header: 'Matrícula', dataIndex: 'matricula', width: 80, renderer: function (value) { return '<div style="text-align:right">' + value + '</div>'; } },
                    { header: 'Nome', dataIndex: 'nome', width: 250 },
                    { header: 'Lotação', dataIndex: 'lotacao', width: 180 },
                    { header: 'Cod. VDF', dataIndex: 'cod_vdf', width: 180 },
                    {header: 'Enviado', dataIndex: 'enviado', width: 65, renderer: toolkit.util.formatStatus},
                ]
            );
        return this._columnModel;
    },

    getToolbar: function (cfg) {
        if(!this._toolbar) {
            var itensTollBar = this.getConfigItemsToolbar(cfg);
            itensTollBar.splice(
                4, 0,
                {
                    xtype: 'button',
                    iconCls: 'icon-siatu icon-siatu-move-down',
                    style: 'margin-top: 10px',
                    text: 'Gerar Relatório',
                    width: 100,
                    height: 25,
                    scope: this,
                    menu: [
                        {
                            text: 'Arquivo PDF ',
                            type: 'PDF',
                            iconCls: 'icon-ged icon-ged-application-pdf',
                            scope: this,
                            handler: function (item) {
                                let periodosItens = this.getPeriodoMenuItemsAtualizado()
                                let periodo = periodosItens.filter(objeto =>objeto.checked == true)
                                if (periodo)
                                    periodo = periodo[0].id
                                this._gerarRelatorioSemestral(periodo,'PDF');
                            }
                        },
                        {
                            text: 'Arquivo DOCX',
                            type: 'DOCX',
                            iconCls: 'icon-ged icon-ged-application-msword',
                            scope: this,
                            handler: function (item) {
                                let periodosItens = this.getPeriodoMenuItemsAtualizado()
                                let periodo = periodosItens.filter(objeto =>objeto.checked == true)
                                if (periodo)
                                    periodo = periodo[0].id
                                this._gerarRelatorioSemestral(periodo,'DOCX');
                            }
                        }
                    ]
                },
               
            );

            itensTollBar.splice(8, 0, '-');
            itensTollBar.splice(
                9,
                0,
                {
                    text: 'Filtros',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: this.getFiltroMenu()
                }
            );
           
                        
            this._toolbar = Ext._create('Ext.Toolbar', {
                style: cfg.toolbarStyle,
                items: itensTollBar,
            });

            if((this.toolbarHideLabel || cfg.toolbarHideLabel))
                this._toolbar.items.each(
                    function(item) {
                        item.tooltip = (item.tooltip || item.text);

                        if(item.text && core.nullValue(item.hideLabel, true))
                            item.text = null;
                    }
                );
        }

        return this._toolbar;
    },

    _gerarRelatorioSemestral: function(periodo,formato){

        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action('RelatorioSemestralTeletrabalho', 'generate_report'),
            params: {
                periodo:periodo,
                formato:formato
            },
            success: function (request) {
                var obj = Ext.decode(request.responseText);
                if (obj.success){
                    Ext.Msg.show({
                        title: 'Solicitando Relatório',
                        msg: obj.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                    if (obj.download){
                        var RemoteObserver = core.RemoteObserver;
                        var cb = RemoteObserver.on('base-report', {
                            scope: this,
                            fn: function (data) {
                                setTimeout(
                                    function() {
                                        toolkit.util.downloadFile({
                                            url: data.path,
                                            filename: data.filename,
                                            approach: 'download',
                                        });;
                                        RemoteObserver.un('base-report', {scope: this})
                                        setTimeout( function() {
                                            Ext.Ajax.request({
                                                url: toolkit.util.Normalize.controller_action(
                                                    'RelatorioSemestralTeletrabalho',
                                                    'marker'
                                                ),
                                                params: {
                                                    uuid: obj.uuid
                                                },
                                                success: function() {},
                                                failure: function() {},
                                            });
                                        },
                                        2000);
                                    
                                    },
                                    1000
                                );
                            
                            }
                        });
                    }
                    
                }else{
                    Ext.Msg.show({
                        title: 'Error',
                        msg: obj.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }     
            },
            failure: function (request) {
                Ext.Msg.show({
                    msg: 'Ocorreu um erro tentando processar sua requisição, tente novamente mais tarde.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                })
            },
            scope: this
        });
    },

    converterDataFormato: function(input) {
        // Verificar se a entrada está no formato DD/MM/AAAA
        const regex = /^\d{2}\/\d{2}\/\d{4}$/;
        if (!regex.test(input)) {
            console.error('Formato de data inválido. Use DD/MM/AAAA.');
            return null;
        }
    
        // Dividir a string em dia, mês e ano
        const partes = input.split('/');
        const dia = partes[0];
        const mes = partes[1];
        const ano = partes[2];
    
        // Formatar a data como AAAA-MM-DD
        const dataFormatada = `${ano}-${mes}-${dia}`;
    
        return dataFormatada;
    },

    getConfigCustomActions: function(){
        return [
   
            {
                iconCls: 'icon-16px icon-esocial icon-pack-sent',
                tooltip: 'Enviar notificação',
                scope: this,
                handler: function(action, index){ 
                    
                    if (action._store.getAt(index).data.enviado.alt == 'enviado'){

                        Ext.Msg.show({
                            title: this.title,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            msg: 'O Gestor selecionado já enviou o Relatorio Semestral no periodo informado.'
                        });
                        

                    }else{
                        this._enviarNotificacaoEmailItem(action._store.getAt(index).data.pk) ; 
                        
                    }                   
                    
                },
            }
           
        ];
    },


    _enviarNotificacaoEmailItem: function(gestor_pk){
        xt.Msg.show({
            msg: 'Tem certeza que deseja Enviar uma notificação por email?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GestorRelatorioSemestral','enviar_notificacao_email'),
                    params: { 
                        gestor_pk: gestor_pk,
                        periodo_pk: this.getParams().periodo_pk,

                    },
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        icon = obj.success == true ? Ext.Msg.INFO : Ext.Msg.ERROR
                        Ext.Msg.show({
                            width:"400px",
                            title: this.title,
                            icon: icon,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
                        this.getStore().reload();
                    },
                    failure: function() {
                        Ext.Msg.show({
                            title: this.title,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                        });
                    },
                    scope: this
                });
            }
        })
    },



});

core.RestfulGrid.register(
    'rh.teletrabalho.gestor_relatorio_semestral.gestor.Restful',
    'rh.teletrabalho.gestor_relatorio_semestral.gestor.Grid'
);

