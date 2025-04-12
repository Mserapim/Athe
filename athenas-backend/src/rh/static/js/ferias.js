if(typeof(toolkit.rh.ferias) == 'undefined') {
    Ext.ns("toolkit.rh.ferias");
    Ext.Ajax.on('beforerequest', function(conn, obj){if(obj.scope && obj.scope.fnBeforeRequest) obj.scope.fnBeforeRequest(conn, obj);},this);
    Ext.Ajax.on('requestcomplete',  function(conn, response, obj){if(obj.scope && obj.scope.fnRequestComplete) obj.scope.fnRequestComplete(conn, response, obj);},this);
    Ext.Ajax.on('requestexception',  function(conn, response, obj){if(obj.scope && obj.scope.fnExceptionRequest) obj.scope.fnRequestComplete(conn, response, obj);},this);
}

toolkit.rh.ferias.ConflitosWin = Ext.extend(
    Ext.Window,
    {
        getFormPanelConflitosInfo: function(){
            if(!this.conflitosInfoPanel) {
                this.conflitosInfoPanel = new Ext.Panel({
                    title: '',
                    labelWidth: 100,
                    labelAlign: 'left',
                    layout: 'form',
                    region: 'north',
                    split:true,
                    padding: 15,
                    data: this.periods,
                    scope: this,
                    tpl: Ext._create('Ext.XTemplate', [
                        '<p><b>Informações:</b></p><br />',
                       // '<tpl if="info">',
                       //     ' para o período aquisitivo de <b>{info}</b>,',
                       // '</tpl>',
                        '<p>Parcelas analisadas:',
                        '<tpl for=".">',
                            ' <p><b>{periodo}</b></p> ',
                        '</tpl>',
                        '</p>',
                        '<p>Verifique o quadro abaixo para saber se existe(m) conflito(s).</p>',
                        '<p>OBS.: Este ocorrido pode ser motivo de indeferimento de sua parcela por parte da chefia imediata.</p>',
                    ]),
                    listeners:{
                        render: function(){
                            this.ownerCt.conflitosInfoPanel.body.highlight('#c3daf9', {block:true});
                        }
                    }
                });
            }
            return this.conflitosInfoPanel;
        },

        getConflitosStore: function(){
            if(!this.conflitosStore){
                this.conflitosStore= new Ext.data.JsonStore({
                    url: toolkit.util.Normalize.controller_action('FRSMarcacaoFerias','get_conflitos'),
                    root: 'result',
                    fields: [
                        'pk',
                        'servidor',
                        'periodo',
                        'marcado_em',
                        'periodo_aquisitivo',
                        'qtd',
                        'order',
                        'workplace',
                    ],
                    baseParams: { pasus: this.pasus_pk },
                    listeners: {
                        beforeload: function(st, opt){
                        },
                        load:function(st, recs, opt){
                        }
                    }
                });
                this.conflitosStore.load();
            }
            return this.conflitosStore;
        },

        getConflitosListPanel: function(){
            if(!this.conflitosPanel) {
                this.conflitosPanel = new Ext.grid.GridPanel({
                    region: 'center',
                    cm: new Ext.grid.ColumnModel([
                        { header: 'Servidor', dataIndex: 'servidor', width: 240, sortable: false },
                        { header: 'Período', dataIndex: 'periodo', width: 150, sortable: false },
                        { header: 'Marcado em', dataIndex: 'marcado_em', width: 70, sortable: false  },
                        { header: 'Periodo aquisitivo', dataIndex: 'periodo_aquisitivo', width: 100, sortable: false },
                        { header: 'Qtd', dataIndex: 'qtd', width: 30, sortable: false },
                        { header: 'Local', dataIndex: 'workplace', width: 100, sortable: false },
                        { header: 'Ordem', dataIndex: 'order', width: 50, sortable: false },
                    ]),
                    store: this.getConflitosStore(),
                    bbar: new Ext.PagingToolbar({
                        store: this.getConflitosStore(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    })
                });
            }
            return this.conflitosPanel;
        },

        constructor: function(father, pasus, info ) {
            var pasus_pk = [];
            var periods = [];
            Object.keys(pasus).forEach(
                function(item) {
                    pasus_pk.push(pasus[item].pk);
                    periods.push({
                        'info':info,
                        'periodo': pasus[item].data_inicio + ' à '+ pasus[item].data_fim
                    });
                }
            );

            var cf = {
                title: 'Conflito de férias',
                width: 760,
                height: 400,
                closable: true,
                resizable: false,
                border: false,
                layout: 'border',
                modal: true,
                father: father,
                pasus_pk: pasus_pk,
                periods: periods,
            };
            if(father.configuration.pas.servidor)
                cf.title= 'Conflito de férias [ '+ father.configuration.pas.servidor +' ]';
            toolkit.rh.ferias.ConflitosWin.superclass.constructor.call(this, cf);

            this.add(this.getFormPanelConflitosInfo());
            this.add(this.getConflitosListPanel());
        }
    }
);

toolkit.rh.ferias.MarcacaoFerias = Ext.extend(
    Ext.Panel,
    {
        getPASGridPaginator: function() {
            if(!this.gridPaginator) {
                this.gridPaginator = new Ext.PagingToolbar({
                    store: this.getPASGridStore(),
                    displayInfo: true,
                    pageSize: 50,
                    prependButtons: true
                });
            }

            return this.gridPaginator;
        },

        getPASColumnModel: function() {
            if(!this.columnModel) {
                this.columnModel = new Ext.grid.ColumnModel([
                    {dataIndex: 'status', header: 'Status', sortable: false, renderer: toolkit.util.formatStatus},
                    {dataIndex: 'periodo_aquisitivo',header: 'Periodo aquisitivo', sortable: true, width: 100},
                    {dataIndex: 'usufruto_ini', header: 'Usufruto inicio', sortable: false, width: 80},
                    {dataIndex: 'usufruto_fim', header: 'Usufruto fim', sortable: false, width: 80},
                    {dataIndex: 'quantidade_dias', header: 'Adquiridos', sortable: false, width: 70},
                    {dataIndex: 'dias_usufruidos', header: 'Usufruídos', sortable: false, width: 70},
                    {dataIndex: 'paid_days', header: 'Indenizados', sortable: false, width: 70},
                    {dataIndex: 'dias_ausufruir', header: 'a Usufruir', sortable: false, width: 70},
                    {dataIndex: 'dias_agendados', header: 'Agendados', sortable: false, width: 70},
                    {dataIndex: 'situacao', header: 'Situação', sortable: false, width: 250}
                ]);
            }

            return this.columnModel;
        },

        getPASGridStore: function() {
            if(!this.pasGridStore) {
                this.pasGridStore = new Ext.data.JsonStore({
                    fields: [
                        'pk',
                        'periodo_aquisitivo',
                        'servidor',
                        'data_referencia',
                        'quantidade_dias',
                        'dias_marcados',
                        'dias_agendados',
                        'dias_usufruidos',
                        'dias_nao_marcados',
                        'paid_days',
                        'dias_ausufruir',
                        'usufruto_fim',
                        'usufruto_ini',
                        'status',
                        'situacao'
                    ],
                    root: 'result',
                    totalProperty: 'totalRows',
                    url: toolkit.util.Normalize.controller_action('FRSMarcacaoFerias','list'),
                    remoteSort: true,
                    baseParams: {sort: ['-periodo_aquisitivo__ano_aquisicao','-periodo_aquisitivo__periodo'], todos: false},
                    listeners:{
                        scope: this,
                        load: function(st, rec, opts){
                            this.onDeselectPAS(rec);
                            this.selectLastPASSelected();
                        },
                        clear: function(st, recs){
                            alert("CLEAR");
                        }
                    }
                });
                this.pasGridStore.load();
            }

            return this.pasGridStore;
        },

        getPASGridToolbar: function() {
            if(!this.pasGridToolbar) {
                this.act_filtroPas = new Ext.Action({
                    text: 'Todos Períodos',
                    scope: this,
                    itemId: 'act_filtro',
                    enableToggle: true,
                    toggleHandler: function(btn, st){
                        this.pasGridStore.baseParams= {sort: ['-periodo_aquisitivo__ano_aquisicao','-periodo_aquisitivo__periodo'], todos: st}
                        this.pasGridStore.load();
                    },
                    icon: '/' + global.Context + '/static/rh/images/add_ferias.png'
                });
                this.act_help = new Ext.Action({
                    text: 'Ajuda',
                    scope: this,
                    itemId: 'act_help',
                    icon: '/' + global.Context + '/static/rh/images/help.png',
                    handler: function(){
                        var helpWnd= new toolkit.rh.ferias.HelpWizard('FRSMarcacaoFerias',true);
                        helpWnd.show();
                    }
                });

                var buttons = [
                    new Ext.Button(this.act_filtroPas),'-',new Ext.Button(this.act_help),'-',
                ];

                this.pasGridToolbar = new Ext.Toolbar({
                    items: buttons
                });
            }
            return this.pasGridToolbar;

        },

        getSelectedPAS: function(){
            return this.pasGridPanel.getSelectionModel().getSelected();
        },

        getLastSelectedPAS: function(){
            return this.pas;
        },

        onSelectPAS: function(rec){
            this.pas= rec;
            if(this.pasuGridPanel)
                this.pasuGridPanel.setTitle("Parcelas ("+ this.pas.data['periodo_aquisitivo']+")");
            if(this.pasuGridPanel){
                this.pasuGridStore.baseParams= {sort: 'data_inicio', dir: 'ASC', pas: this.pas.data['pk']};
                this.pasuGridStore.load({params: {limit: 10}});
            }
            if(this.pasHistoricoGridStore){
                this.pasHistoricoGridStore.baseParams= {pas: this.pas.data['pk']};
                this.pasHistoricoGridStore.load();
            }
            if(rec.data.quantidade_dias>rec.data.dias_marcados) this.act_novo.enable();
//            if(this.pas.data.status) alert(this.pas.data.status);

        },

        onDeselectPAS: function(rec){
            this.act_novo.disable();
            this.onDeselectPASU(rec);
            this.act_mostrar_todos.toggle(false, false);
        },

        onSelectPASU: function(rec){
            this.pasu= rec;
            this.act_remover.enable();
            this.act_conflitos.enable();
            this.act_alterar.enable();
        },

        onDeselectPASU: function(rec){
            this.pasu= null;
            this.act_remover.disable();
            this.act_conflitos.disable();
            this.act_alterar.disable();
        },

        indexOfPAS: function(rec, id){
            return rec.data.pk == this.pas.data.pk;
        },

        selectLastPASSelected: function(){
            if(this.pas){
                idx = this.getPASGridStore().findBy(function(rec, id){return rec.data.pk==this.pas.data.pk;},this);
                if(idx>=0) this.pasGridPanel.getSelectionModel().selectRow(idx);
            }
        },

        getSelectedPASU: function(){
            if(this.pasuGridPanel.getSelectionModel().getCount()>1)
                return this.pasuGridPanel.getSelectionModel().getSelections();
            else return this.pasuGridPanel.getSelectionModel().getSelected();
        },

        _novo: function(){
            pas = this.getSelectedPAS();
            scope = this;
            if(pas){
                new toolkit.rh.ferias.GerenciamentoPASUs(
                    pas.data,
                    [],
                    {
                        father: this,
                        acao: 'marcar',
                        title: 'Marcação de férias',
                        callback: function(){scope.refresh_pas();}
                    }
                ).show();
            }else{
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Você deve selecionar um período antes de tentar marcar uma parcela!',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
            }
        },

        _conflitos: function(){
            pas = this.getSelectedPAS();
            pasu = this.getSelectedPASU();
            if(pasu){
                this.configuration.pas = pas.data;
                var pasus = [];
                this.pasuGridPanel.getSelectionModel().getSelections().forEach(
                    function(item) {
                        pasus.push({
                            pk: item.data.pk,
                            conflict: item.data.conflict,
                            data_inicio: item.data.data_inicio,
                            data_fim: item.data.data_fim
                        });
                    }
                );

                new toolkit.rh.ferias.ConflitosWin(
                    this,
                    pasus,
                    pas.data.periodo_aquisitivo
                ).show();
            }else{
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Você deve selecionar uma parcela para verificar os conflitos!',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
            }
        },

        _alterar: function(){
            pas = this.getSelectedPAS();
            pasus = this.pasuGridPanel.getSelectionModel().getSelections();
            scope= this;
            if(pasus){
                new toolkit.rh.ferias.GerenciamentoPASUs(
                    pas.data,
                    pasus,
                    {
                        father: this,
                        acao: 'alterar',
                        title: 'Solicitação de alteração de férias',
                        callback: function(){
                            scope.refresh_pas();
                    }
                    }
                ).show();
            }else{
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Você deve selecionar uma parcela antes de tentar alterá-la!',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
            }
        },

        _remover: function(){
            pasu = this.getSelectedPASU();
            pas= this.getSelectedPAS();
            if(pasu){
                Ext.MessageBox.show({
                    title: 'Atenção',
                    msg: 'Tem certeza que deseja excluir esta parcela?',
                    fn: function(btn, text){
                        if(btn=='yes'){
                            Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action(
                                    'FRSMarcacaoFerias',
                                    'marcacao'
                                ),
                                params: {acao:'desmarcar',pas: pas.data.pk, pasu: pasu.data.pk},
                                success: function(request) {
                                    var result = Ext.decode(request.responseText);
                                    if(result.success)
                                        this.refresh_pas();
                                    else{
                                        Ext.MessageBox.show({
                                           title: 'Erro ao desmarcar parcela',
                                           msg: result.error,
                                           buttons: Ext.MessageBox.OK,
                                           icon: Ext.MessageBox.ERROR
                                        });
                                    }
                                },
                                failure: function(request) {
                                    if(request && request.result && request.result.error) {
                                        Ext.MessageBox.show({
                                           title: 'Erro de conexão',
                                           msg: request.result.error,
                                           buttons: Ext.MessageBox.OK,
                                           icon: Ext.MessageBox.ERROR
                                        });
                                    }
                                },
                                scope: this
                            })

                        }
                    },
                    buttons: Ext.MessageBox.YESNO,
                    icon: Ext.MessageBox.WARNING,
                    scope: this
                 });
            }else{
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Você deve selecionar uma parcela antes de tentar desmarcá-la!',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
            }
        },

        getPASUGridPaginator: function() {
            if(!this.pasuGridPaginator) {
                this.pasuGridPaginator = new Ext.PagingToolbar({
                    store: this.getPASUGridStore(),
                    displayInfo: true,
                    pageSize: 50,
                    prependButtons: true
                });
            }

            return this.pasuGridPaginator;
        },

        getPASUGridToolbar: function() {
            if(!this.pasuGridToolbar) {
                this.act_novo = new Ext.Action({
                    text: 'Marcar Parcela',
                    scope: this,
                    handler: this._novo,
                    iconCls: true,
                    itemId: 'act_novo',
                    icon: '/' + global.Context + '/static/rh/images/add_ferias.png',
                    disabled: true
                });
                this.act_remover = new Ext.Action({
                    text: 'Desmarcar Parcela',
                    scope: this,
                    handler: this._remover,
                    iconCls: true,
                    itemId: 'act_remover',
                    icon: '/' + global.Context + '/static/rh/images/remove_ferias.png',
                    disabled: true
                });
                this.act_conflitos = new Ext.Action({
                    text: 'Verificar Conflitos',
                    scope: this,
                    handler: this._conflitos,
                    iconCls: true,
                    itemId: 'act_conflitos',
                    icon: '/' + global.Context + '//static/rh/images/ferias_conflito.png',
                    disabled: true
                });
                this.act_alterar = new Ext.Action({
                    text: 'Solicitar Alteração',
                    scope: this,
                    handler: this._alterar,
                    iconCls: true,
                    itemId: 'act_alterar',
                    icon: '/' + global.Context + '/static/rh/images/alter_ferias.png',
                    disabled: true
                });
                this.act_mostrar_todos = new Ext.Button(new Ext.Action({
                    text: 'Todos',
                    scope: this,
                    iconCls: true,
                    itemId: 'act_mostrar_todos',
                    icon: '/' + global.Context + '/static/rh/images/add_ferias.png',
                    enableToggle: true,
                    toggleHandler: function(btn, st){
                        this.pasuGridStore.baseParams.todos = st;
                        this.pasuGridStore.load();
                    }
                }));

                var buttons = [
                    new Ext.Button(this.act_novo),new Ext.Button(this.act_remover),'-',
                    new Ext.Button(this.act_conflitos),'-',
                    new Ext.Button(this.act_alterar),'-',
                    this.act_mostrar_todos,'-'
                ];

                this.pasuGridToolbar = new Ext.Toolbar({
                    items: buttons
                });
            }
            return this.pasuGridToolbar;

        },

        getPASUColumnModel: function() {
            if(!this.pasuColumnModel) {
                this.pasuColumnModel = new Ext.grid.ColumnModel([
                    {dataIndex: 'status', header: 'Status', sortable: false, renderer: toolkit.util.formatStatus},
                    {dataIndex: 'data_inicio',header: 'Data inicial', sortable: true, width: 150},
                    {dataIndex: 'data_fim', header: 'Data final', sortable: false, width: 150},
                    {dataIndex: 'dias', header: 'Dias', sortable: false, width: 80},
                    {dataIndex: 'situacao', header: 'Situação', sortable: false, width: 150},
                    {dataIndex: 'criado_por', header: 'Criado por', sortable: false, width: 85},
                    {dataIndex: 'criado_em', header: 'Criado em', sortable: false, width: 85},
                    {dataIndex: 'modificado_por', header: 'Modificado por', sortable: false, width: 85},
                    {dataIndex: 'modificado_em', header: 'Modificado em', sortable: false, width: 85},
                ]);
            }

            return this.pasuColumnModel;
        },

        getPASUGridStore: function() {
            if(!this.pasuGridStore) {
                this.pasuGridStore = new Ext.data.JsonStore({
                    fields: [
                        'status',
                        'pk',
                        'data_inicio',
                        'data_fim',
                        'dias',
                        'situacao',
                        'criado_por',
                        'criado_em',
                        'modificado_por',
                        'modificado_em',
                    ],
                    root: 'result',
                    totalProperty: 'totalRows',
                    url: toolkit.util.Normalize.controller_action('FRSPeriodoAquisitivoServidorUsufruto','list'),
                    remoteSort: true
                });

            }
            return this.pasuGridStore;
        },

        refresh: function() {alert("REFRESH")},

        refresh_pasu: function() {this.getPASUGridStore().reload();},

        refresh_pas: function() {this.getPASGridStore().reload();},

        getTabPanel:function(){
            if(!this.tabPanel){
                this.tabPanel = new Ext.TabPanel({
                    defaults:{
                        layout: {
                            type:'vbox',
                            padding:'5',
                            align:'stretch'
                        },
                        margins:'0 0 5 0'
//                        autoHeight: true
                    },
                    border: true,
                    activeTab: 0,
                    flex: 1,
                    items:[
                        this.getPASUGridPanel(),
                    ],
                    listeners:{
                        activate: function(p){
                        }
                    }
                });
            }
            return this.tabPanel;
        },

        getPASGridPanel: function() {
            if(!this.pasGridPanel) {
                this.pasGridPanel = new Ext.grid.GridPanel({
                    title: "<b>Selecione o período desejado...</b>",
                    store: this.getPASGridStore(),
                    cm: this.getPASColumnModel(),
                    border: true,
//                    boxMinHeight:180,
                    flex: 1,
                    sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                    listeners: {
                        scope: this
                    },
                    tbar: this.getPASGridToolbar(),
                    bbar: this.getPASGridPaginator(),
                    loadMask: new Ext.LoadMask(Ext.getBody(), {msg:"Carregando informações..."})

                });

            }

            return this.pasGridPanel;
        },

        getPASUGridPanel: function() {
            if(!this.pasuGridPanel) {
                this.pasuGridPanel = new Ext.grid.GridPanel({
                    title: "Parcelas",
                    store: this.getPASUGridStore(),
                    cm: this.getPASUColumnModel(),
                    flex: 1,
                    listeners: {
                        scope: this
                    },
                    bbar: this.getPASUGridPaginator(),
                    tbar: this.getPASUGridToolbar()
                });
            }

            return this.pasuGridPanel;
        },

        constructor: function() {
            var cf = {
                title: 'Marcação de Férias',
                closable: true,
                layout: {
                    type:'vbox',
                    padding:'5',
                    align:'stretch'
                },
                configuration: {
                    pas: null,
                    callback: function(){}
                },
                defaults:{margins:'0 0 5 0'}
            };

            toolkit.rh.ferias.MarcacaoFerias.superclass.constructor.call(this, cf);

            this.add(this.getPASGridPanel());
            this.add(this.getTabPanel());


// ----------------- LISTERNERS -------------------------------------------------
            this.pasGridPanel.getSelectionModel().on(
                "rowselect",
                function(sm, index, rec) {
                    this.onSelectPAS(rec);
                },
                this
            );
            this.pasuGridPanel.getSelectionModel().on(
                "rowselect",
                function(sm, index, rec) {
                    this.onSelectPASU(rec);
                },
                this
            );
            this.pasGridPanel.getSelectionModel().on(
                "rowdeselect",
                function(sm, index, rec) {
                    this.onDeselectPAS(rec);
//                    alert(rec.data['pk']);
                },
                this
            );
// ----------------- LISTERNERS -------------------------------------------------
            var active = toolkit.Application.tabspace.getActiveTab();
            toolkit.Application.tabspace.remove(active);
            toolkit.Application.tabspace.add(this);

        }
    }
);


toolkit.rh.ferias.InfoPasu = Ext.extend(
    Ext.Window,
    {

        getFieldSetPasuInfo: function(pasu){
            if(!this.fsPasuInfo){
                this.fsPasuInfo = new Ext.form.FieldSet({
                    xtype: 'fieldset',
                    title: 'Parcela/Usufruto',
                    layout: 'form',
                    id: 'fs_parcela',
                    items: [{
                            xtype: 'displayfield',
                            fieldLabel: 'Início/fim usufruto',
                            value: this.pasu['periodo'],
                            anchor: '100%',
                            name: 'pasu_periodo'
                        },{
                            xtype: 'displayfield',
                            fieldLabel: 'Dias',
                            value: this.pasu['dias'],
                            anchor: '100%',
                            name: 'pasu_dias'
                        }
                    ]
                });
            }
            return this.fsPasuInfo;
        },

        getFieldSetAlteracaoInfo: function(){
            if(!this.fsAlteracaoInfo){
                var antigos_pasus = {};
                var novos_pasus = {};
                var items = new Array();
                if(this.pasu.novos){
                    items = new Array();
                    for( var i= 0; i< this.pasu.novos.length; i++){
                        items.push({
                            xtype: 'panel',
                            anchor: '100%',
                            layout: 'column',
                            border: false,
                            items:[{
                                columnWidth: .9,
                                layout: 'form',
                                border: false,
                                items:[{
                                    xtype: 'displayfield',
                                    fieldLabel: (i+1)+'ª Parcela',
                                    value: this.pasu.novos[i]['data_inicio']+ ' à '+this.pasu.novos[i]['data_fim']+ ' ('+this.pasu.novos[i]['dias']+' dias)',
                                    anchor: '100%',
                                    name: 'antigo_'+i
                                }]
                            },{
                                columnWidth: .1,
                                border: false,
                                items:[{
                                    xtype: 'button',
                                    scope: this,
                                    idx_pasu: i,
                                    handler: function(bt, ev){
                                        new toolkit.rh.ferias.ConflitosWin(
                                            this,
                                            [{
                                                pk: this.pasu.novos[bt.idx_pasu].pk,
                                                conflict: this.pasu.novos[bt.idx_pasu].conflict,
                                                data_inicio: this.pasu.novos[bt.idx_pasu].data_inicio,
                                                data_fim: this.pasu.novos[bt.idx_pasu].data_fim
                                            }],
                                            false).show();
                                    },
                                    iconCls: true,
                                    itemId: 'act_verificar',
                                    icon: '/' + global.Context + '/static/rh/images/ferias_conflito.png'
                                }]
                            }]
                        });
                    }
                    novos_pasus = {
                        xtype: 'fieldset',
                        title: 'Nova(s) Parcela(s)',
                        items:[items]
                    }
                }
                if(this.pasu.antigos){
                    items = new Array();
                    for( i= 0; i< this.pasu.antigos.length; i++){
                        items.push({
                                xtype: 'displayfield',
                                fieldLabel: (i+1)+'ª Parcela',
                                value: this.pasu.antigos[i]['data_inicio']+ ' à '+this.pasu.antigos[i]['data_fim']+ ' ('+this.pasu.antigos[i]['dias']+' dias)',
                                anchor: '100%',
                                name: 'novo_'+i
                            });
                    }
                    antigos_pasus = {
                        xtype: 'fieldset',
                        title: 'Parcela(s) a ser(em) alterada(s)',
                        items:[items]
                    }

                }

                this.fsAlteracaoInfo = new Ext.form.FieldSet({
                    title: 'Informações sobre a Alteração',
                    layout: 'form',
                    id: 'fs_alteracao',
                    items:[
                        antigos_pasus,
                        novos_pasus,{
                            xtype: 'displayfield',
                            fieldLabel: 'Época oportuna',
                            value: this.pasu['epoca_oportuna'] + ' dias',
                            anchor: '100%',
                            name: 'epoca_oportuna'
                        },{
                            xtype: 'displayfield',
                            fieldLabel: 'Justificativa',
                            value: this.pasu['justificativa'],
                            anchor: '100%',
                            name: 'justificativa'
                        }
                    ]
                });
            }
            return this.fsAlteracaoInfo;
        },

        getFormPanelInfo: function() {
            if(!this.formPanelInfo) {
                var buttons = [{
                    text: 'Fechar',
                    anchor: '45%',
                    handler: this.destroy,
                    scope: this
                }]

                this.formPanelInfo = new Ext.form.FormPanel({
                    labelWidth: 100,
                    labelAlign: 'left',
                    layout: 'auto',
                    autoHeight:true,
                    padding: 5,
                    width: 400,
                    items:[{
                        xtype: 'fieldset',
                        title: 'Informações sobre o período',
                        layout: 'form',
                        animCollapse: true,
                        collapsible: true,
                        items: [{
                                xtype: 'displayfield',
                                fieldLabel: 'Servidor',
                                value: this.pas['servidor'],
                                anchor: '100%',
                                name: 'servidor'
                            },{
                                xtype: 'displayfield',
                                fieldLabel: 'Período',
                                value: this.pas['periodo_aquisitivo'],
                                anchor: '100%',
                                name: 'periodo'
                            },{
                                xtype: 'displayfield',
                                fieldLabel: 'Dias agendados',
                                value: this.pas['dias_agendados'],
                                anchor: '100%',
                                name: 'dias_agendados'
                            },{
                                xtype: 'displayfield',
                                fieldLabel: 'Dias a marcar',
                                value: this.pas['dias_nao_marcados'],
                                anchor: '100%',
                                name: 'dias_restantes'
                            },{
                                xtype: 'displayfield',
                                fieldLabel: 'Dias usufruídos',
                                value: this.pas['dias_usufruidos'],
                                anchor: '100%',
                                name: 'dias_usufruidos'
                            },{
                                xtype: 'displayfield',
                                fieldLabel: 'Início para fruição',
                                value: this.pas['data_ini_usufruto'],
                                anchor: '100%',
                                name: 'dias_usufruidos'
                            }
                        ]
                    }],
                    buttons: buttons
                });
                if(this.pasu.emalteracao) this.formPanelInfo.add(this.getFieldSetAlteracaoInfo());
                else this.formPanelInfo.add(this.getFieldSetPasuInfo());
            }

            return this.formPanelInfo;
        },

        constructor: function(pas, pasu) {
            var cf = {
                title: "Informação de parcela de férias",
                closable: true,
                resizable: false,
                configuration:{pas: pas},
                pas: pas,
                pasu: pasu,
                modal: true
            };

            toolkit.rh.ferias.InfoPasu.superclass.constructor.call(this, cf)

            this.add(this.getFormPanelInfo());
        }
    }
);


toolkit.rh.ferias.AutorizacaoFerias = Ext.extend(
    Ext.Panel,
    {
        getPASUGridPaginator: function() {
            if(!this.pasuGridPaginator) {
                this.pasuGridPaginator = new Ext.PagingToolbar({
                    store: this.getPASUGridStore(),
                    displayInfo: true,
                    pageSize: 20,
                    prependButtons: true
                })
            }

            return this.pasuGridPaginator;
        },

        getPASUColumnModel: function() {
            if(!this.pasuColumnModel) {
                this.pasuColumnModel = new Ext.grid.ColumnModel([
                    {dataIndex: 'status', header: 'Status', sortable: false, width: 80, renderer: toolkit.util.formatStatus},
                    {dataIndex: 'pa', header: 'Período', sortable: true, width: 100},
                    {dataIndex: 'servidor', header: 'Servidor', sortable: true, width: 300},
                    {dataIndex: 'data_inicio',header: 'Data inicial', sortable: true, width: 85},
                    {dataIndex: 'data_fim', header: 'Data final', sortable: false, width: 85},
                    {dataIndex: 'criado_por', header: 'Criado por', sortable: false, width: 85},
                    {dataIndex: 'criado_em', header: 'Criado em', sortable: false, width: 85},
                    {dataIndex: 'modificado_por', header: 'Modificado por', sortable: false, width: 85},
                    {dataIndex: 'modificado_em', header: 'Modificado em', sortable: false, width: 85},
                    {dataIndex: 'dias', header: 'Dias', sortable: false, width: 35},
                    {dataIndex: 'situacao', header: 'Situação', sortable: false, width: 150},
                    {dataIndex: 'lotacao', header: 'Lotação', sortable: false, width: 250},
                    {dataIndex: 'chefia', header: 'Chefia', sortable: true, width: 250}
                ]);
            }

            return this.pasuColumnModel;
        },

        getPASUGridStore: function() {
            if(!this.pasuGridStore) {
                this.pasuGridStore = new Ext.data.JsonStore({
                    autoLoad: true,
                    fields: [
                        'pk',
                        'status',
                        'conflict',
                        'new_pasus',
                        'pa',
                        'servidor',
                        'data_inicio',
                        'data_fim',
                        'dias',
                        'situacao',
                        'lotacao',
                        'alteracao',
                        'chefia',
                        'criado_por',
                        'criado_em',
                        'modificado_por',
                        'modificado_em',
                    ],
                    root: 'result',
                    totalProperty: 'totalRows',
                    url: toolkit.util.Normalize.controller_action(this.configuration.controller,'list'),
                    remoteSort: true,
                    listeners:{
                        scope: this,
                        load: function(st, rec, opts){
                            this.selectLastPASUSelected();
                        }
                    }
                });

                this.pasuGridStore.load({
                    params: {
                        sort: 'pa',
                        limit: 20,
                        start: 0,
                        dir: 'ASC'
                    }
                });
            }

            return this.pasuGridStore;
        },

        getPASUGridPanel: function() {
            if(!this.pasuGridPanel) {
                this.pasuGridPanel = new Ext.grid.GridPanel({
                    title: "<b>Selecione o período desejado...</b>",
                    store: this.getPASUGridStore(),
                    cm: this.getPASUColumnModel(),
                    border: true,
                    flex: 2,
                    sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                    listeners: {
                        scope: this
                    },
                    bbar: this.getPASUGridPaginator(),
                    tbar: this.getPASUGridToolbar(),
                    loadMask: new Ext.LoadMask(Ext.getBody(), {msg:"Carregando informações..."})
                });

            }

            return this.pasuGridPanel;
        },

        getPASUGridToolbar: function() {
            if(!this.pasuGridToolbar) {
                this.act_autorizar = new Ext.Action({
                    text: 'Deferir',
                    scope: this,
                    handler: this._autorizar,
                    iconCls: true,
                    itemId: 'act_autorizar',
                    icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                    disabled: true
                });
                this.act_indeferir = new Ext.Action({
                    text: 'Indeferir',
                    scope: this,
                    handler: this._desautorizar,
                    iconCls: true,
                    itemId: 'act_indeferir',
                    icon: '/' + global.Context + '/static/rh/images/pasu_nao_autorizado.png',
                    disabled: true
                });
                this.act_verificar = new Ext.Action({
                    text: 'Verificar Conflitos',
                    scope: this,
                    handler: this._verificar,
                    iconCls: true,
                    itemId: 'act_verificar',
                    icon: '/' + global.Context + '/static/rh/images/ferias_conflito.png',
                    disabled: true
                });
                this.act_notificar = new Ext.Action({
                    text: 'Notificar Conflito',
                    scope: this,
                    handler: this._notificar,
                    iconCls: true,
                    itemId: 'act_informar',
                    icon: '/' + global.Context + '/static/rh/images/notificado.png',
                    disabled: true
                });
                this.act_info = new Ext.Action({
                    text: 'Informação',
                    scope: this,
                    handler: this._info,
                    iconCls: true,
                    itemId: 'act_info',
                    icon: '/' + global.Context + '/static/rh/images/notificado.png',
                    disabled: true
                });

                this.findText = new Ext.form.TextField({
                    width: 280,
                    enableKeyEvents: true,
                    emptyText: 'Informe o texto a ser pesquisado e clique em Localizar.',
                    listeners: {
                        scope: this,
                        keypress: function(text, event) {
                            if (event.getCharCode() == event.RETURN || event.getCharCode() == event.TAB) {
                                this.setFilter();
                            }
                        }
                    }
                });

                var buttons = [{
                        text: 'Autorização',
                        icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                        menu:{
                            items:[
                                this.act_autorizar,
                                this.act_indeferir
                            ]
                        }
                    },
                    '-',
                    new Ext.Button(this.act_info),
                    '-',
                    new Ext.Button(this.act_notificar),
                    '-',
                    new Ext.Button(this.act_verificar),
                    '-',
                    new Ext.form.Label({text: 'Localizar:'}),
                    this.findText,
                    {
                        xtype: 'button',
                        text: 'Limpar',
                        iconCls: true,
                        icon: '/' + global.Context + '/static/images/clean.png',
                        handler: function() {
                            this.findText.setValue(undefined);
                            this.setFilter();
                        },
                        scope: this
                    }
                ];

                this.pasuGridToolbar = new Ext.Toolbar({
                    items: buttons
                });
            }
            return this.pasuGridToolbar;

        },

        setFilter: function() {
            var store = this.getPASUGridStore();
            var keyword = this.findText.getValue();

            if (keyword != undefined && keyword != '') {
                store.baseParams.keyword = keyword;
            }
            else {
                store.baseParams.keyword = undefined;
            }
            store.reload({
                params: {
                    sort: 'pa',
                    limit: 20,
                    start: 0,
                    dir: 'ASC'
                }
            });
        },

        getSelectedPASU: function(){
            return this.pasuGridPanel.getSelectionModel().getSelected();
        },

        getLastSelectedPASU: function(){
            return this.pasu
        },

//      TODO dry this code
        _notificar: function(){
            pasu = this.getSelectedPASU();
//            pas= this.getSelectedPA();
            scope= this;
            if(pasu){
                new toolkit.rh.ferias.Notificacao(
                    this,
                    pasu.data,
                    function(){scope.refresh_pas();}
                ).show();
            }else{
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Você deve selecionar uma parcela antes de tentar autorizá-la!',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
            }

        },
//      TODO dry this code
        _desautorizar: function(){
            this.autorizarPASU(false);
        },

        _autorizar: function(){
            this.autorizarPASU(true);
        },

        autorizarPASU: function(deferir){
            pasu = this.getSelectedPASU();
//            pas= this.getSelectedPA();
            if(pasu){
                Ext.MessageBox.show({
                    title: 'Atenção',
                    msg: 'Tem certeza que deseja '+(deferir==true? 'deferir': 'indeferir')+' esta parcela?',
                    fn: function(btn, text){
                        if(btn=='yes'){
                            Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action(
                                    'FRSAutorizacaoFerias',
                                    'autorizacao'
                                ),
                                params: {acao:(deferir==true? 'autorizar': 'desautorizar'), pasu: pasu.data.pk},
                                success: function(request) {
                                    var result = Ext.decode(request.responseText);
                                    if(result.success)
                                        this.refresh_pas();
                                    else{
                                        Ext.MessageBox.show({
                                           title: 'Erro ao autorizar parcela',
                                           msg: result.error,
                                           buttons: Ext.MessageBox.OK,
                                           icon: Ext.MessageBox.ERROR
                                        });
                                    }
                                },
                                failure: function(request) {
                                    if(request && request.result && request.result.error) {
                                        Ext.MessageBox.show({
                                           title: 'Erro de conexão',
                                           msg: request.result.error,
                                           buttons: Ext.MessageBox.OK,
                                           icon: Ext.MessageBox.ERROR
                                        });
                                    }
                                },
                                scope: this
                            })

                        }
                    },
                    buttons: Ext.MessageBox.YESNO,
                    icon: Ext.MessageBox.WARNING,
                    scope: this
                 });
            }else{
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Você deve selecionar uma parcela antes de tentar autorizá-la!',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
            }
        },

        _verificar: function(){
            pasu = this.getSelectedPASU();
            if(pasu){
                if(Object.keys(pasu.data.new_pasus).length > 0)
                    var pasus = pasu.data.new_pasus;
                else{
                    var pasus = [{
                        pk: pasu.data.pk,
                        conflict: pasu.data.conflict,
                        data_inicio: pasu.data.data_inicio,
                        data_fim: pasu.data.data_fim
                    }];
                }
                new toolkit.rh.ferias.ConflitosWin(this, pasus, false).show();
            }else{
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Você deve selecionar uma parcela para verificar os conflitos!',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
            }
        },

        _info:function(){
            pasu = this.getSelectedPASU();
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    'FRSAutorizacaoFerias',
                    'get_info'
                ),
                params: {pasu: pasu.data.pk},
                success: function(request) {
                    var result = Ext.decode(request.responseText);
                    if(result.success){
                        new toolkit.rh.ferias.InfoPasu(
                            result.result.pas,
                            result.result.pasu
                        ).show();
                    }else{
                        Ext.MessageBox.show({
                           title: 'Erro ao pesquisar parcela',
                           msg: result.message,
                           buttons: Ext.MessageBox.OK,
                           icon: Ext.MessageBox.ERROR
                        });
                    }
                },
                failure: function(request) {
                    if(request && request.result && request.result.error) {
                        Ext.MessageBox.show({
                           title: 'Erro de conexão',
                           msg: request.result.error,
                           buttons: Ext.MessageBox.OK,
                           icon: Ext.MessageBox.ERROR
                        });
                    }
                },
                scope: this
            });
        },

        onSelectPASU: function(rec){
            this.pasu= rec;
            this.act_autorizar.enable();
            this.act_indeferir.enable();
            this.act_verificar.enable();
            this.act_notificar.enable();
            this.act_info.enable();
            this.configuration.pas = {'servidor':rec.data.servidor};
        },

        onDeselectPASU: function(rec){
            this.pasu= null;
            this.act_autorizar.disable();
            this.act_indeferir.disable();
            this.act_verificar.disable();
            this.act_notificar.disable();
            this.configuration.pas= null;
        },

        selectLastPASUSelected: function(){
            if(this.pasu){
                idx= this.getPASUGridStore().findBy(function(rec, id){return rec.data.pk==this.pasu.data.pk;},this)
                if(idx>=0) this.pasuGridPanel.getSelectionModel().selectRow(idx);
            }
        },

        refresh_pas: function() {this.getPASUGridStore().reload();},

        constructor: function(cfg) {
            if(!cfg) cfg={};
            var cf = {
                title: cfg.title || 'Autorização de Férias',
                closable: true,
                layout: {
                    type:'vbox',
                    padding:'5',
                    align:'stretch'
                },
                configuration: {
                    pas: cfg.pas || null,
                    callback: cfg.callback || function(){},
                    controller: cfg.controller || 'FRSAutorizacaoFerias'
                },
                defaults:{margins:'0 0 5 0'}

            };

            toolkit.rh.ferias.AutorizacaoFerias.superclass.constructor.call(this, cf);

            this.add(this.getPASUGridPanel());


// ----------------- LISTERNERS -------------------------------------------------
            this.pasuGridPanel.getSelectionModel().on(
                "rowselect",
                function(sm, index, rec) {
                    this.onSelectPASU(rec);
                },
                this
            );
            this.pasuGridPanel.getSelectionModel().on(
                "rowdeselect",
                function(sm, index, rec) {
                    this.onDeselectPASU(rec);
                },
                this
            );
// ----------------- LISTERNERS -------------------------------------------------
            var active = toolkit.Application.tabspace.getActiveTab();
            toolkit.Application.tabspace.remove(active);
            toolkit.Application.tabspace.add(this);

        }
    }
);

//---------------------------------------------------------------------------
toolkit.rh.ferias.AutorizacaoFeriasMembros = Ext.extend(
    toolkit.rh.ferias.AutorizacaoFerias,
    {
        constructor: function(){
            toolkit.rh.ferias.AutorizacaoFeriasMembros.superclass.constructor.call(this, {title: 'Autorização de Férias - Membros', controller:'FRSAutorizacaoFeriasChefiaMembros'});
        }
    }
);

//---------------------------------------------------------------------------
toolkit.rh.ferias.AutorizacaoFeriasAdmin = Ext.extend(
    toolkit.rh.ferias.AutorizacaoFerias,
    {
        constructor: function(){
            toolkit.rh.ferias.AutorizacaoFeriasAdmin.superclass.constructor.call(this, {title: 'Autorização de Férias - Admin', controller:'FRSAutorizacaoFeriasChefiaAdmin'});
        }
    }
);

//----------------------------------------------------------------------------
    toolkit.rh.ferias.Notificacao = Ext.extend(
        Ext.Window,
        {
            getFormPanel: function() {
                if(!this.formPanel) {
                    this.formPanel = new Ext.form.FormPanel({
                        frame: true,
                        border: false,
                        defaults: {
                            width: '420'
                        },
                        items: [
                            {
                                html: '<p><b>Você deseja notificar esse conflito? Caso deseje, digite a mensagem a ser enviada ou utilize a mensagem padrão!</b></p>'
                            },
                            {
                                name: 'mensagem',
                                xtype: 'textarea',
                                hideLabel:true,
                                editable: true,
                                emptyText: "Digite a mensagem a ser notificada ou envie usando a mensagem padrão..."
                            }
                        ]
                    });
                }

                return this.formPanel
            },

            constructor: function(father, pasu, callback) {

                var cf = {
                    title: 'Notificação - Conflito de Férias',
                    closable: true,
                    resizable: false,
                    modal: true,
                    border: false,
                    width: 500,
                    configuration: {
                        pasu: pasu,
                        callback: callback || function(){}
                    },
                    buttons: [
                        {
                            text: 'Enviar',
                            scope: this,
                            handler: this.commit
                        },
                        {
                            text: 'Cancelar',
                            scope: this,
                            handler: this.destroy
                        }
                    ]
                };

                toolkit.rh.ferias.Notificacao.superclass.constructor.call(this, cf);

                this.add(this.getFormPanel());
            },

            commit: function() {
                var form = this.getFormPanel().getForm();

                form.waitMsgTarget = this.getEl();
                form.submit({
                    waitMsg: 'Enviando notificação...',
                    url: toolkit.util.Normalize.controller_action(
                        'FRSAutorizacaoFerias',
                        'autorizacao'
                    ),
                    params: {
                        pasu: this.configuration.pasu.pk,
                        acao: 'notificar'
                    },
                    success: function(form, request) {
                        this.configuration.callback(request.result.result);
                        this.destroy();
                    },
                    failure: function() {
                        alert('Não foi possivel notificar conflito.');
                    },
                    scope: this
                })
            }
        }
    );

//----------------------------------------------------------------------------
toolkit.rh.ferias.HelpWizard = Ext.extend(
    Ext.Window,
    {
        fnBeforeRequest: function(conn, obj){
          if(this.getEl())
            this.getEl().mask('Carregando...');
        },
        fnRequestComplete: function(conn, response, obj){
          if(this.getEl())
            this.getEl().unmask();
        },
        fnExceptionRequest: function(conn, response, obj){
        },
        _sendToRemote: function(controller, action, fnSuccess, params){
            /*
             *
             *
             *
             */
            Ext.Ajax.request({
                url: toolkit.util.Normalize.controller_action(
                    controller,
                    action
                ),
                params: params,
                success: function(request) {
                    var result = Ext.decode(request.responseText);
                    if(result.success){
                        fnSuccess(result, this);
                    }else{
                        Ext.MessageBox.show({
                           title: "Ironia - Erro na Ajuda",
                           msg: "Houve um erro na aquisição da ajuda, informe ao administrador do sistema!",
                           buttons: Ext.MessageBox.OK,
                           icon: Ext.MessageBox.ERROR
                        });
                    }
                },
                failure: function(request) {
                    var result = Ext.decode(request.responseText);
                    if(result.error) {
                        Ext.MessageBox.show({
                           title: 'Erro de conexão',
                           msg: result.error,
                           buttons: Ext.MessageBox.OK,
                           icon: Ext.MessageBox.ERROR
                        });
                    }
                },
                scope: this
            })

        },
        onGetHelpInfoSuccess: function(result, scope){
            if( result && result.items){
                scope.add(result.items);
                scope.config.total = result.total+1;
            }
        },
        onGetHelpSuccess: function(result, scope){
            if( result && result.item){
                scope.add(result.item);
                scope.navToIndex(scope.items.length -1);
            }
        },
        _getHelpInfo: function(){
            /*
             */
            this._sendToRemote(this.config.controller, this.config.actGetHelpInfo, this.onGetHelpInfoSuccess);
        },
        _getHelp: function(index){
            /*
             */
            res = this._sendToRemote(this.config.controller, this.config.actGetHelp, this.onGetHelpSuccess, {'index':index})
        },
        navToIndex: function(index){
            this.layout.setActiveItem(index);
            if(this.items.indexOfKey(this.layout.activeItem.id) == this.config.total-1){
                next.disable();
            }else if(this.items.indexOfKey(this.layout.activeItem.id) == 0){
                prev.disable();
            }else{
                next.enable();
                prev.enable();
            }
        },
        navHandler: function(direction){
            console.debug(this);
            console.debug(this.layout);
            console.debug(this.layout.activeItem);
            console.debug(this.layout.activeItem.id);
            bbar = this.getBottomToolbar();
            next= bbar.get('move-next');
            prev= bbar.get('move-prev');
            if((this.items.indexOfKey(this.layout.activeItem.id)+direction+1)>this.items.length){
                this._getHelp(this.items.indexOfKey(this.layout.activeItem.id)+direction);
            }else{
                this.navToIndex(this.items.indexOfKey(this.layout.activeItem.id)+direction);
            }

            // This routine could contain business logic required to manage the navigation steps.
            // It would call setActiveItem as needed, manage navigation button state, handle any
            // branching logic that might be required, handle alternate actions like cancellation
            // or finalization, etc.  A complete wizard implementation could get pretty
            // sophisticated depending on the complexity required, and should probably be
            // done as a subclass of CardLayout in a real-world implementation.
        },
        constructor: function(controller, remote, cfg){
            /*
             *@controller: nome do controller que conterá os métodos 'get_help_info' e 'get_help'
             *@cfg: configurações para o componente e para o window
             *  @@cache(true*|false): se as telas carregadas remotamente são cacheadas no componente
             *  @@actGetHelpInfo: nome do action no @controller que será chamado por _getHelpInfo
             *      return um json: {total: qtde_de_telas, @cfg,(items:[{id: }])}
             *
             *
             */
            cfg = cfg || {};
            var cf= {
                scope: this,
                title: cfg.title || 'Ajuda do Athenas',
                layout:'card',
                activeItem: 0, // make sure the active item is set on the container config!
                width: cfg.width || 500,
                height: cfg.height || 400,
                autoScroll: true,
                id: 'helpWnd',
                defaults: {
                    autoScroll: true,
                    bodyStyle: 'padding:15px',
                    cls:'content-help',
                    style: {
                        color: '#15428b'
                    }
                },
                config:{
                    controller: controller,
                    remote: true,
                    cache: cfg.cache || true,
                    total: 1,
                    callback: cfg.callback || function(){},
                    actGetHelp: cfg.get_help || 'get_help_item',
                    actGetHelpInfo: cfg.get_help_info || 'get_help_info'
                },
                bbar: [
                    {
                        id: 'move-prev',
                        text: 'Anterior',
                        handler: this.navHandler.createDelegate(this, [-1]),
                        disabled: true
                    },
                    '->', // greedy spacer so that the buttons are aligned to each side
                    {
                        id: 'move-next',
                        text: 'Próximo',
                        handler: this.navHandler.createDelegate(this, [1])
                    }
                ],
                items: [{
                    id: 'passo-0',
                    html: '<p style="text-align:center;"><img width="300" height="307" src="/' + global.Context + '/static/images/help/help_athenas_passo0.png" /></p>'
                }],
                listeners:{
                    scope: this,
                    close: function(){
                        this.destroy();
                    }
                }
            };
            toolkit.rh.ferias.HelpWizard.superclass.constructor.call(this, cf);
            this._getHelpInfo();
        }
    }
)
