Ext._define('rh.gestorenvioponto.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gestorenvioponto.Window',

    configOrderToolBar: ['search' ],

    hideActions: ['edit', 'remove', 'copy'],

    hideItemsToolbar: ['add', 'remove', 'edit'],

    ano: new Date().getFullYear(),
    mes: new Date().getMonth(),

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Matrícula', dataIndex: 'matricula', width: 80 },
                    { header: 'Nome', dataIndex: 'nome', width: 250, id: 'autoExpandColumn' },
                    { header: 'Lotação', dataIndex: 'lotacao', width: 200 },
                    { header: 'Categoria Funcional', dataIndex: 'categoria_funcional', width: 150 },
                    { header: 'Aprovador', dataIndex: 'aprovador', width: 150 },
                    { header: 'Data Admissão', dataIndex: 'dt_admissao', width: 100 },
                    { header: 'Status', dataIndex: 'status', width: 150 },
                    { header: 'Cód. VDF', dataIndex: 'cod_vdf', width: 80 },
                    { header: 'Teletrabalho', dataIndex: 'in_teletrabalho', width: 80 },
                    { header: 'Afastamento', dataIndex: 'tipo_afastamento', width: 150 },
                    { header: 'Último Envio', dataIndex: 'ultimo_envio', width: 100 },
                    { header: 'Qtd. Notificações', dataIndex: 'qtd_notificacoes', width: 100 },
                    { header: 'Chave', dataIndex: 'servidor_pk', width: 100, hidden: true },
                    { header: 'Enviado Em', dataIndex: 'enviado_em', width: 100, renderer: Ext.util.Format.dateRenderer('d/m/Y'), hidden: true },
                    { header: 'Aprovado Em', dataIndex: 'aprovado_em', width: 100, renderer: Ext.util.Format.dateRenderer('d/m/Y'), hidden: true },
                    { header: 'Efetivado Em', dataIndex: 'efetivado_em', width: 100, renderer: Ext.util.Format.dateRenderer('d/m/Y'), hidden: true },
                ]
            );

        return this._columnModel;
    },

    getConfigCustomActions: function(){
        var cfg = this
        return [
   
            {
                iconCls: 'icon-16px icon-esocial icon-pack-sent',
                tooltip: 'Enviar notificação',
                scope: this,
                handler: function(action, index){

                    var status = action._store.getAt(index).data.status;
                    var teletrabalho = action._store.getAt(index).data.in_teletrabalho;
                    var record = action._store.getAt(index);

                    if (status === 'Efetivado') {
                        Ext.Msg.show({
                            title: cfg.title,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            msg: 'A folha de ponto para este servidor já foi efetivada para a competência selecionada.'
                        });
                    } else if (status === 'Isento de envio') {
                        Ext.Msg.show({
                            title: cfg.title,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            msg: 'Este servidor está isento do envio da folha de ponto para a competência selecionada.'
                        });
                    } else if (teletrabalho === 'SIM'){
                        Ext.Msg.show({
                            title: cfg.title,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK,
                            msg: 'O envio da folha de ponto não é obrigatório porque o servidor tem teletrabalho ativo durante a competência selecionada.'
                        });
                    } else {
                        this._enviarNotificacaoEmailItem(record);
                    }
                },
            }
           
        ];
    },

    _enviarNotificacaoEmailItem: function(record) {
        Ext.Msg.show({
            msg: 'Tem certeza que deseja enviar uma notificação por email?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;
                var matricula = record.data.matricula;
                var ultimo_envio = record.data.ultimo_envio;
                var aprovador = record.data.aprovador;
    
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('RHGestorEnvioPontos', 'enviar_notificacao_email'),
                    params: { 
                        mes: this.mes,
                        ano: this.ano,
                        matricula: matricula,
                        ultimo_envio: ultimo_envio,
                        aprovador: aprovador
                    },
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        icon = obj.success == true ? Ext.Msg.INFO : Ext.Msg.ERROR
                        Ext.Msg.show({
                            width: "400px",
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
                            msg: 'Recurso indisponível no momento, tente novamente mais tarde.'
                        });
                    },
                    scope: this
                });
            }
        });
    },

    getNotificacaoEmailMassaAction: function () {
        if (!this._notificacaoEmailMassaAction)
            this._notificacaoEmailMassaAction = Ext._create('Ext.Button', {
                iconCls: 'icon-16px icon-esocial icon-pack-sent',
                tooltip: 'Enviar notificação em massa',
                scope: this,
                handler: function () {
                   this._notificacaoMassaAction('enviar_notificacao_em_massa')
                },
            });

        return this._notificacaoEmailMassaAction;
    },


    _notificacaoMassaAction: function(method){
        params = {
            "mes":this.getStore().baseParams['periodo_mes'] ,
            "ano":this.getStore().baseParams['periodo_ano'] ,
            "teletrabalho":this.getStore().baseParams['teletrabalho'],
            "status":this.getStore().baseParams['status'],
            "notificado":this.getStore().baseParams['notificado'],
            "posses":this.getStore().baseParams['posses']
        }

        Ext.Msg.show({
            msg: 'Tem certeza que deseja enviar notificação em massa por email?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('RHGestorEnvioPontos', method),
                    params,
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        var icon = obj.success == true ? Ext.Msg.INFO : Ext.Msg.ERROR;
                        Ext.Msg.show({
                            width:"400px",
                            title: this.title,
                            icon: icon,
                            buttons: Ext.Msg.OK,
                            msg: obj.message
                        });
        
                        if(obj.success == true){ 
                            this.getStore().reload(); 
                        }
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
        });

    },


    getToolbar: function(cfg) {
        if(!this._toolbar) {
            var itensTollBar = this.getConfigItemsToolbar(cfg);

            itensTollBar.splice(
                3, 0,
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
                                this._gerarRelatorio('PDF')
                            }
                        },
                        {
                            text: 'Arquivo CSV',
                            type: 'CSV',
                            iconCls: 'icon-esocial icon-reports-icons',
                            scope: this,
                            handler: function (item) {
                                this._gerarRelatorio('CSV');
                            }
                        },
                        {
                            text: 'Arquivo XLS',
                            type: 'XLS',
                            iconCls: 'icon-esocial icon-csv-icons',
                            scope: this,
                            handler: function (item) {
                
                                this._gerarRelatorio('XLS');
                            }
                        }
                    ]
                },
               
            );

            itensTollBar.splice(4, 0,'-');
            itensTollBar.splice(5, 0, 'Mês: ');
            itensTollBar.splice(6, 0, this.comboMes());
            itensTollBar.splice(7, 0, '-');
            itensTollBar.splice(8, 0, 'Ano: ');
            itensTollBar.splice(9, 0, this.comboAno());

            itensTollBar.splice(10, 0, '<p style="font-weight: bold;">Notificar em Massa: </p>');
            itensTollBar.splice(11, 0, this.getNotificacaoEmailMassaAction());

            var menuFiltroStatus = this.menuFiltroStatus();
            itensTollBar.splice(
                12,
                0,
                {
                    text: 'Filtro por Status',
                    emptyText: 'Status',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: menuFiltroStatus,
                }
            )
            itensTollBar.splice(15, 0, '-');
            var menuFiltroTeletrabalho = this.menuFiltroTeletrabalho();
            itensTollBar.splice(
                13,
                0,
                {
                    text: 'Filtro por Teletrabalho',
                    emptyText: 'Teletrabalho',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: menuFiltroTeletrabalho,
                }
            )
            itensTollBar.splice(17, 0);           
            var menuFiltroPosse = this.menuFiltroPosse();
            itensTollBar.splice(
                14,
                0,
                {
                    text: 'Filtro Tipo Posse',
                    emptyText: 'Tipo de Posse',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: menuFiltroPosse,
                }
            )

            itensTollBar.splice(18, 0);           
            var menuFiltroNotificacao = this.menuFiltroNotificacao();
            itensTollBar.splice(
                15,
                0,
                {
                    text: 'Filtro pro notificação',
                    emptyText: 'Notificação',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: menuFiltroNotificacao,
                }
            )

            this._toolbar = Ext._create('Ext.Toolbar', {
                style: cfg.toolbarStyle,
                items: itensTollBar,
            });
        }

        return this._toolbar;
    },


    _gerarRelatorio: function(formato){
        params = {
            "mes":this.getStore().baseParams['periodo_mes'] ,
            "ano":this.getStore().baseParams['periodo_ano'] ,
            "teletrabalho":this.getStore().baseParams['teletrabalho'],
            "status":this.getStore().baseParams['status'],
            "notificado":this.getStore().baseParams['notificado'],
            "posses":this.getStore().baseParams['posses'],
            "formato":formato
        }
        if ('keyword' in this.getStore().baseParams )
            params["keyword"] = this.getStore().baseParams['keyword']

        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action('GestorFolhaPonto', 'generate_report'),
            params,
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
                                                    'GestorFolhaPonto',
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

    filtroMesAno: function(){

        this._toolbar.items.items.forEach(function(item, i){
            if(item.emptyText == 'Ano para filtro') { 
                this.ano = item.getValue(); 
            }
            if(item.emptyText == 'Mês para filtro') { 
                this.mes = item.getValue(); 
            }
        });

        this.getStore().baseParams['periodo_ano'] = this.ano;
        this.getStore().baseParams['periodo_mes'] = this.mes;

        this.getStore().load();
    },

    comboAno: function(){
        const timeElapsed = Date.now();
        const hoje = new Date(timeElapsed);

        return {
            xtype: 'combo',
            id: 'comboAno',
            store: new Ext.data.JsonStore({
                proxy: new Ext.data.HttpProxy({
                    url: toolkit.util.Normalize.controller_action('RHGestorEnvioPontos', 'anos_folha_ponto'),
                    disableCaching: true,
                    method: 'GET'
                }),
                root: 'root',
                fields: ['pk', 'descricao']
            }),
            displayField: 'descricao',
            valueFeild: 'pk',
            emptyText: 'Ano para filtro',
            width: 140,
            triggerAction: 'all',
            value: hoje.getFullYear(),
            listeners: {
                scope: this,
                select: function (combo, record) {
                    this.ano = record.json.pk;
                    var mesCombo = Ext.getCmp('comboMes');
                    this.mes = mesCombo.getValue();
                    if (this.mes) {
                        this.filtroMesAno(this.ano, this.mes);  
                    }
                }
            }
        }
    },

    comboMes: function(){
        const timeElapsed = Date.now();
        const hoje = new Date(timeElapsed);
        const mesAtual = hoje.getMonth() + 1;

        return {
            xtype: 'combo',
            id: 'comboMes',
            store: [
                [1, 'JANEIRO'],
                [2, 'FEVEREIRO'],
                [3, 'MARÇO'],
                [4, 'ABRIL'],
                [5, 'MAIO'],
                [6, 'JUNHO'],
                [7, 'JULHO'],
                [8, 'AGOSTO'],
                [9, 'SETEMBRO'],
                [10, 'OUTUBRO'],
                [11, 'NOVEMBRO'],
                [12, 'DEZEMBRO'],
            ],
            emptyText: 'Mês para filtro',
            width: 140,
            triggerAction: 'all',
            value: mesAtual === 1 ? 12 : mesAtual - 1,
            listeners: {
                scope: this,
                select: function (combo, record) {
                    this.mes = record.json[0];
                    var anoCombo = Ext.getCmp('comboAno');
                    this.ano = anoCombo.getValue();

                    this.filtroMesAno(this.ano, this.mes);
                }
            },
        }
    },

    menuFiltroStatus: function() {
        this._menuFiltroStatus = [
            {
                id: 'todos',
                text: 'Todos',
                checked: true,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarStatus(chk, 'todos') },
            },
            {
                id: 'nao_criado',
                text: 'Não criado',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarStatus(chk, 'nao_criado') },
            },
            {
                id: 'aguardando_aprovador',
                text: 'Aguardando aprovador',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarStatus(chk, 'aguardando_aprovador') },
            },
            {
                id: 'aguardando_efetivacao',
                text: 'Aguardando efetivação',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarStatus(chk, 'aguardando_efetivacao') },
            },
            {
                id: 'efetivado',
                text: 'Efetivado',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarStatus(chk, 'efetivado') },
            },
            {
                id: 'isento',
                text: 'Isento de envio',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarStatus(chk, 'isento') },
            },
        ];
        return this._menuFiltroStatus;
    },
    
    filtrarStatus: function(chk, opcao) {
        var filtros_aplicar = [];
        cfg =  this

        this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item) {
            if (item.id === opcao) {
                if (!chk.checked == true) {
                    if (item.id === 'todos') {
                        filtros_aplicar.push('todos');
                    } else if (item.id === 'aguardando_aprovador') {
                        filtros_aplicar.push('aguardando_aprovador');
                    } else if (item.id === 'aguardando_efetivacao') {
                        filtros_aplicar.push('aguardando_efetivacao');
                    } else if (item.id === 'efetivado') {
                        filtros_aplicar.push('efetivado');
                    } else if (item.id === 'nao_criado') {
                        filtros_aplicar.push('nao_criado');
                    } else if (item.id === 'isento') {
                        filtros_aplicar.push('isento');
                    }
                } 
            } else {
                item.setChecked(false);
            }
        });

        cfg.getStore().baseParams['status'] = filtros_aplicar;
        
        cfg.getStore().load();
        return filtros_aplicar
    },

    menuFiltroTeletrabalho: function() {
        this._menuFiltroTeletrabalho = [
            {
                id: 'teletrabalho_sim',
                text: 'SIM',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarTeletrabalho(chk, 'teletrabalho_sim') },
            },
            {
                id: 'teletrabalho_nao',
                text: 'NÃO',
                checked: true,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarTeletrabalho(chk, 'teletrabalho_nao') },
            }
            
        ];
        return this._menuFiltroTeletrabalho;
    },


    filtrarTeletrabalho: function(chk, opcao) {
        var filtros_aplicar = [];
        cfg =  this

        this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item) {
            if (item.id === opcao) {
                if (!chk.checked == true) {
                    if(item.id === 'teletrabalho_sim'){
                        filtros_aplicar.push('teletrabalho_sim');
                    }
                    else if(item.id === 'teletrabalho_nao'){
                        filtros_aplicar.push('teletrabalho_nao');
                    }
                }
            } else {
                item.setChecked(false);
            }
        });

        cfg.getStore().baseParams['teletrabalho'] = filtros_aplicar;
        
        cfg.getStore().load();
    },


    menuFiltroNotificacao: function() {
        this._menuFiltroNotificacao = [
            {
                id: 'todos_notificados',
                text: 'Todos',
                checked: true,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarNotificacao(chk, 'todos_notificados') },
            },
            {
                id: 'sim',
                text: 'Sim',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarNotificacao(chk, 'sim') },
            },
            {
                id: 'nao',
                text: 'Não',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarNotificacao(chk, 'nao') },
            }
            
        ];
        return this._menuFiltroNotificacao;
    },

    filtrarNotificacao: function(chk, opcao) {
        var filtros_aplicar = [];
        cfg =  this

        this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item) {
            if (item.id === opcao) {
                if (!chk.checked == true) {
                    if(item.id === 'todos_notificados'){
                        filtros_aplicar.push('todos_notificados');
                    }
                    else if(item.id === 'sim'){
                        filtros_aplicar.push('sim');
                    }
                    else if(item.id === 'nao'){
                        filtros_aplicar.push('nao');
                    }
                }
            } else {
                item.setChecked(false);
            }
        });

        cfg.getStore().baseParams['notificado'] = filtros_aplicar;
        
        cfg.getStore().load();
    },

    menuFiltroPosse: function(){
        this._menuFiltroPosse = [
            {
                id: 'EFE',               
                value: 'EFE',               
                text: 'EFETIVO',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarPosse(chk, 'EFE') },
            },
            {
                id: 'EFC',
                value: 'EFC',
                text: 'EFETIVO com FC',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarPosse(chk, 'EFC') },
            },
            {
                id: 'ECM',
                value: 'ECM',
                text: 'EFETIVO com CM',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarPosse(chk, 'ECM') },
            },
            {
                id: 'CMS',
                value: 'CMS',
                text: 'COMISSIONADO',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarPosse(chk, 'CMS') },
            },
            {
                id: 'REQ',
                value: 'REQ',
                text: 'REQUISITADO',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarPosse(chk, 'REQ') },
            },
            {
                id: 'REX',
                value: 'REX',
                text: 'REQUISITADO EXTERNO',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarPosse(chk, 'REX') },
            },
            {
                id: 'RCM',
                value: 'RCM',
                text: 'REQUISITADO com CM',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarPosse(chk, 'RCM') },
            },
            {
                id: 'RFC',
                value: 'RFC',
                text: 'REQUISITADO com FC',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarPosse(chk, 'RFC') },
            },
            {
                id: 'EST',
                value: 'EST',
                text: 'ESTAGIÁRIO',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarPosse(chk, 'EST') },
            },
            {
                id: 'VOL',
                value: 'VOL',
                text: 'VOLUNTÁRIO',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarPosse(chk, 'VOL') },
            },
            {
                id: 'EXT',
                value: 'EXT',
                text: 'EXTERNO SEM VÍNCULO',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarPosse(chk, 'EXT') },
            },
            {
                id: 'RES',
                value: 'RES',
                text: 'RESIDENTES',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.filtrarPosse(chk, 'RES') },
            },      
        ]
        return this._menuFiltroPosse;
    },

    filtrarPosse: function(chk, opcao) {
        var filtros_aplicar = [];
        if(opcao == 'todos'){
            if(!chk.checked == true){
                this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                    if(item.id != 'todos' && item.checked == true){
                        item.setChecked(false);
                    }
                });
            } else {
                this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                    if(item.id != 'todos' && item.checked == true){
                        filtros_aplicar.push(item.value);
                    }
                });
                if(filtros_aplicar.length == 0){
                    filtros_aplicar.push(true);
                    this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                        if(item.id == 'EFE'){ item.setChecked(true); }
                    });
                }
            }
        } else {
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                if(item.id == 'todos' && item.checked == true){
                    item.setChecked(false);
                } else if (
                    (item.id != 'todos' && item.id == opcao && !chk.checked == true) ||
                    (item.id != 'todos' && item.id != opcao && item.checked == true)
                ) {
                    filtros_aplicar.push(item.value);
                }
            });
        }

        this.getStore().baseParams['posses'] =  JSON.stringify(filtros_aplicar)
        
        if(filtros_aplicar.length > 0){
            this.setFilterProperty('type_by_possession__in', filtros_aplicar, 1001, true);
        } else {
            this._toolbar.activeMenuBtn.menu.items.items.forEach(function(item){
                if(item.id == 'todos' && !chk.checked == false){
                    item.setChecked(true);
                }
            });
            this.removeFilterProperty('type_by_possession__in', 1001, true);
        }
        this.getStore().reload();
    },

    doDownload: function() {
        var config = {
            filter: Ext.encode(this.getFilter()),
            keyword: this.getKeywordField().getValue(),
            teletrabalho: this.getStore().baseParams['teletrabalho'],
            status: this.getStore().baseParams['status'],
            periodo_ano: this.ano,
            periodo_mes: this.mes,
            start: 0,
            limit: this.getStore().getTotalCount(),
            format: 'text/csv'
        };
        var rest = this.factoryRestful();
        var url = rest.getRoute('export').url + '?' + Ext.urlEncode(config);

        window.open(url, '_self');
    },
    
});

core.RestfulGrid.register(
    'rh.gestorenvioponto.Restful',
    'rh.gestorenvioponto.Grid'
);