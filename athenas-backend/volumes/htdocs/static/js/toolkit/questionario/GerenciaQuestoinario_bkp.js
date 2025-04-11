Ext.ns('toolkit.questionario');
toolkit.questionario.icons = '/' + CONTEXT + '/static/workflow/icons/';


toolkit.questionario.GerenciaQuestionario = Ext.extend(
	toolkit.widget.TabPanel,
    {
        constructor: function(cfg){
            cfg = cfg?cfg:{};
            Ext.applyIf(cfg, {
                title:'Questionários',
                layout:'fit',
                items:this._getQuestionarioGrid() //getgrid
            });
            toolkit.questionario.GerenciaQuestionario.superclass.constructor.call(this,cfg);

            this._questionarioGrid.getSelectionModel().on(
                "rowselect",
                function(sm, index, rec) {
                    this.onSelectQuest(rec);
                   //console.debug(rec);
                   //console.debug(this._getSelectedQuest());
                   // Ext.Msg.alert('Seleção', 'linha selecionada'+ index);
                },
                this
            );
          

        },

        getToolBar: function(){
            if(!this.ToolBar) {
                this.act_novo = new Ext.Action({
                    text: 'Novo',
                    scope: this,
                    handler: this._novo,
                    iconCls: true,
                    itemId: 'act_novo',
                    icon: toolkit.questionario.icons+'add.png',
                    disabled: false
                });
                this.act_editar = new Ext.Action({
                    text: 'Editar',
                    scope: this,
                    handler: this._editar,
                    iconCls: true,
                    itemId: 'act_editar',
                    icon: toolkit.questionario.icons+'edit.png',
                    disabled: true
                });
                
                this.act_excluir = new Ext.Action({
                    text: 'Excluir',
                    scope: this,
                    itemId: 'act_excluir',
                    icon: '/' + global.Context + '/static/rh/images/delete.png',
                    disabled:true,
                    handler: this._excluir
                });
                
                var buttons = [
                    '-',
                    new Ext.Button(this.act_novo),
                    '-',
                    new Ext.Button(this.act_editar),
                    '-',
                    new Ext.Button(this.act_excluir)
                ];

                this.ToolBar = new Ext.Toolbar({
                    items: buttons
                });
            }
            return this.ToolBar;

        },

        getOtherGridToolbar: function() {
            if(!this.pasuOtherToolbar) {
                this.act_questionario = new Ext.Action({
                    text: 'Questionário',
                    scope: this,
                    handler: this._questao,
                    iconCls: true,
                    itemId: 'act_questionario',
                    //icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                    disabled: false
                });
                this.act_alternativas = new Ext.Action({
                    text: 'Alternativas',
                    scope: this,
                    handler: this._questao,
                    iconCls: true,
                    itemId: 'act_alternativas',
                    //icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                    disabled: false
                });
                this.act_ref_textual = new Ext.Action({
                    text: 'Referência Textual',
                    scope: this,
                    handler: this._questao,
                    iconCls: true,
                    itemId: 'act_ref_textual',
                    //icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                    disabled: false
                });
                this.act_questao = new Ext.Action({
                    text: 'Questão',
                    scope: this,
                    handler: this._questao,
                    iconCls: true,
                    itemId: 'act_questao',
                    //icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                    disabled: false
                });
                this.act_autorizar = new Ext.Action({
                    text: 'Questão MS',
                    scope: this,
                    handler: this._autorizar,
                    iconCls: true,
                    itemId: 'act_autorizar',
                    //icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                    disabled: false
                });
                this.act_indeferir = new Ext.Action({
                    text: 'Questão Enum',
                    scope: this,
                    handler: this._desautorizar,
                    iconCls: true,
                    itemId: 'act_indeferir',
                    //icon: '/' + global.Context + '/static/rh/images/pasu_nao_autorizado.png',
                    //disabled: true
                });
                this.act_indeferir1 = new Ext.Action({
                    text: 'Questão Aberta',
                    scope: this,
                    handler: this._desautorizar,
                    iconCls: true,
                    itemId: 'act_indeferir1',
                    //icon: '/' + global.Context + '/static/rh/images/pasu_nao_autorizado.png',
                    //disabled: true
                });
                this.act_help = new Ext.Action({
                    text: 'Ajuda',
                    scope: this,
                    itemId: 'act_help',
                    icon: '/' + global.Context + '/static/rh/images/help.png',
                    disabled:true,
                    handler: function(){
                        var scope = this;
                        new toolkit.widget.ExtCrudForm(
                            {
                                controller: 'QQuestionario',
                                reload_grid: function() {
                                    scope.refresh();
                                }
                            },
                            toolkit.widget.ExtCrudForm.TYPE.NEW
                        ).show();

                    }
                });
                
                var buttons = [{
                        text: 'Gerenciar',
                        icon: '/' + global.Context + '/static/rh/images/pasu_autorizado.png',
                        /*menu:{
                            items:[
                                this.act_questao,
                                this.act_autorizar,
                                this.act_indeferir,
                                this.act_indeferir1
                            ]
                        }*/
                        split: true,
                        defaultStyle: 'splitbutton',
                        menu:[
                                this.act_questionario,
                                this.act_alternativas,
                                this.act_ref_textual,
                                //this.act_indeferir1,
                                {
                                    text: 'Questões',
                                    menu:[
                                        this.act_questao,
                                        this.act_autorizar,
                                        this.act_indeferir,
                                        this.act_indeferir1
                                    ]
                                }
                        ]
                    },
                    '-',
                    {
                        tooltip:'Criar Questionário.',
                        icon: toolkit.questionario.icons+'add.png',
                        text: 'Novo',
                        handler: function(){
                            var form = Ext.getCmp('form-questionario');
                            if (!form)
                            {
                               form = this._getForm(); 
                               var window = new Ext.Window({
                                    title:'Novo',
                                    items:[form]
                                });
                                window.show();
                            }
                        },
                        scope:this
                    },
                    /*'-',
                    new Ext.Button(this.act_info),
                    */'-',
                    new Ext.Button(this.act_help)
                ];

                this.pasuOtherToolbar = new Ext.Toolbar({
                    items: buttons
                });
            }
            return this.pasuOtherToolbar;

        },

        reload_grid: function(params){
            if(this.store)
                this.store.load({
                    param: params || {}
                });
            else
                alert("Bug: ExtCrud: O reload só pode ser evocado quando o grid estiver criado.");
        },

        _novo: function(){
            var form = Ext.getCmp('form-questionario');
                            if (!form)
                            {
                               form = this._getForm(); 
                               var window = new Ext.Window({
                                    title:'Novo',
                                    items:[form]
                                });
                                window.show();
                            }
            /*pas = this._getSelectedQuest();
            scope = this;
            if(pas){
                var scope = this;
                        new toolkit.widget.ExtCrudForm(
                            {
                                controller: 'QQuestao',
                                reload_grid: function() {
                                    scope.refresh();
                                }
                            },
                            toolkit.widget.ExtCrudForm.TYPE.NEW
                        ).show();
            }else{
                Ext.MessageBox.show({
                   title: 'Informação',
                   msg: 'Você deve selecionar um período antes de tentar marcar uma parcela!',
                   buttons: Ext.MessageBox.OK,
                   icon: Ext.MessageBox.INFO
                });
            }*/
          
        },

        _editar: function(){

                    /*new toolkit.widget.ExtCrudForm(
                        {
                            controller: 'FRSPeriodoAquisitivo',
                            reload_grid: function() {
                                this.refresh();
                            }
                        },
                        toolkit.widget.ExtCrudForm.TYPE.EDIT,
                        this.getSelectedPAS().data.periodo_aquisitivo_pk,
                        [
                            {'name':'ano_aquisicao', 'value':null, 'enabled':false},
                            {'name':'periodo', 'value':null, 'enabled':false},
                            {'name':'configuracao', 'value':null, 'enabled':false},
                            {'name':'mes_fruicao', 'value':null, 'enabled':false}
                        ]
                    ).show();*/

        },

        _excluir: function(grid, row, col){

            console.debug(grid);
            var record = this._getSelectedQuest();

            xConfirm({
            title:'Confirmação',
            msg:'Confirma a exclusão deste questionario: '+ record.get('titulo') +' ?',
            fn: function(btn)
            { toolkit.questionario.delete(grid, 'QQuestionário/delete/json', {id:record.get('id')}); }
            });
        },

        _getQuestionarioToolbar: function(){
            var barra = [

                    {
                        tooltip:'Criar Questionário.',
                        icon: toolkit.questionario.icons+'add.png',
                        text: 'Novo',
                        scope:this,
                        handler: function(){
                            var form = Ext.getCmp('form-questionario');
                            if (!form)
                            {
                               form = this._getForm(); 
                               var window = new Ext.Window({
                                    title:'Novo',
                                    items:[form]
                                });
                                window.show();
                            }
                        }
                    },
                    '-',
                    {
                        tooltip:'Editar Questionário.',
                        icon: toolkit.questionario.icons+'edit.png',
                        text: 'Editar',
                        disabled:true,
                        handler: function(){
                            alert('asdf');

                        }
                    },
                    '-',
                    {
                        tooltip:'Excluir Questionário.',
                        icon: toolkit.questionario.icons+'delete.png',
                        text: 'Excluir',
                        scope:this,
                        handler: function(grid, row, col){

                            console.debug(grid);
                            var record = this._getSelectedQuest();

                            xConfirm({
                                title:'Confirmação',
                                msg:'Confirma a exclusão deste questionario: '+ record.get('titulo') +' ?',
                                fn: function(btn)
                                { toolkit.questionario.delete(grid, 'QQuestionário/delete/json', {id:record.get('id')}); }
                            });

                        }
                    }
                ]
            return barra;
        },

        _getQuestionarioStore: function(){
         
            if(!this._questionarioStore)
            {
                this._questionarioStore = new Ext.data.JsonStore({
                    autoLoad:true,
                    root: 'result',
                    totalProperty: 'total',
                    fields: ['id', 'titulo', 'data_inicio','data_fim','ativo'],
                    //url: toolkit.util.Normalize.controller_action('FernandoCRUD','list'),
                    proxy: new Ext.data.HttpProxy({
                        method:'GET',
                        url: action('QQuestionario/list/json')
                    }),                
                    scope:this
                });
            }
            return this._questionarioStore;

        },

        _getQuestionarioGrid: function(){
            if(!this._questionarioGrid)
            {
                this._questionarioGrid = new Ext.grid.GridPanel({
                    scope:this,
                    border:true,
                    store: this._getQuestionarioStore(),
                    columns: 
                    [
                        {
                            dataIndex:'id', 
                            header:'Chave', 
                            width:100
                        },
                        {
                            dataIndex:'titulo', 
                            header:'Titulo', 
                            width:300
                        },
                        {
                            dataIndex:'data_inicio', 
                            header:'Data Inicio', 
                            width:180
                        },
                        {
                            dataIndex:'data_fim', 
                            header:'Data Fim', 
                            width:180
                        },
                        {
                            dataIndex:'ativo', 
                            header:'Ativo',
                            width:100, 
                            renderer: function(value){
                                if (value == true)
                                    return 'Sim'
                                else
                                    return 'Não'
                            }
                        },
                        {
                            xtype:'actioncolumn',
                            header:'Controles',
                            width: 80,
                            scope:this,
                            items:
                            [
                                {
                                    tooltip:'Questionário',                                
                                    icon: '/' + global.Context + '/static/rh/images/detalhes.png',
                                    handler: function(grid, row, col)
                                    {
                                        
                                        var record = grid.getStore().getAt(row);
                                        //console.log(record.get('titulo'));
                                        var win = this.getPanel();
                                        win.setTitle('Questionário: ' + record.get('titulo'));
                                        win.show();
                                        
                                    },
                                    scope:this
                                }
                            ]
                        }
                    ],
                    tbar: this.getToolBar(),
                    //tbar:this._getQuestionarioToolbar(),
                    //tbar:this.getOtherGridToolbar(),
                    bbar:[this._getQuestionarioPagination()]
                });

            }
            return this._questionarioGrid;

        },

        _getQuestionarioPagination: function(){
            if(!this._questionarioPagination)
            {
                this._questionarioPagination = new Ext.PagingToolbar({
                    store: this._getQuestionarioStore(),
                    displayInfo: true,
                    pageSize: 15,
                    prependButtons: true
                });

            }
            return this._questionarioPagination;
        },

        _getForm: function(opts){

            var formQ = new Ext.form.FormPanel({
                id:'form-questionario',
                autoHeight:true,
                width:500,
                closable:true,
                scope:this,
                items:[
                    {
                        xtype:'textfield',
                        fieldLabel:'Titulo',
                        name:'titulo',
                        //allowBlank: false,
                        //value:opts.vals.name || '',
                        width:300
                    },
                    {
                        xtype:'xhtmleditor',
                        fieldLabel:'Descrição',
                        name:'descricao',
                        editable: true,
                        //value:opts.vals.name || '',
                        width:300
                    },
                    {
                        xtype:'datefield',
                        "format": "d/m/Y",
                        fieldLabel:'Data Início',
                        name:'data_inicio',
                        allowBlank: false,
                        //value:opts.vals.name || '',
                        width:300
                    },
                    {
                        xtype:'datefield',
                        "format": "d/m/Y",
                        fieldLabel:'Data Fim',
                        name:'data_fim',
                        allowBlank: false,
                        //value:opts.vals.name || '',
                        width:300
                    },
                    {
                        xtype:'checkbox',
                        fieldLabel:'Ativo',
                        checked:true,
                        inputValue:1,
                        name: 'cb_ativo'
                    }
                    ,
                    {
                        xtype:'checkbox',
                        fieldLabel:'Único',
                        //inputValue:1,
                        name: 'cb_unico'
                    }
                ],
                buttons:[
                {
                    text:'Enviar',
                    handler: function()
                    {
                        formQ.getForm().submit({
                            url:action('QQuestionario/save/json'),
                            success: function(form, action) {
                               Ext.Msg.alert('Sucesso', action.result.msg);
                            },
                            failure: function(form, action) {
                                switch (action.failureType) {
                                    case Ext.form.Action.CLIENT_INVALID:
                                        Ext.Msg.alert('Failure', 'Form fields may not be submitted with invalid values');
                                        break;
                                    case Ext.form.Action.CONNECT_FAILURE:
                                        Ext.Msg.alert('Failure', 'Ajax communication failed');
                                        break;
                                    case Ext.form.Action.SERVER_INVALID:
                                       Ext.Msg.alert('Erro', action.result.msg);
                               }
                            }
                        })
                    }
                }
            ]
            });
            return formQ;
        },

        _getSelectedQuest: function(){
            return this._questionarioGrid.getSelectionModel().getSelected();
            //return this._questionarioGrid.getSelectionModel().getSelections()
        },

        onSelectQuest: function(rec){
            this.quest= rec;
            this.act_editar.enable();
            this.act_excluir.enable();
            //this.configuration.pas = {'servidor':rec.data.servidor};
        },

        getPanel: function(){
            
                var _panel = new Ext.Window({
                title: 'Tela de teste 02',
                width:700, 
                height:400,
                scope:this,
                autoScroll:true,
                items:[
                    {
                    layout:'form',
                    xtype: 'fieldset',
                    title: 'Informações',
                    layout: 'form',
                    /*items:[
                        xtype: 'displayfield',
                        fieldLabel: 'Teste'
                    ]*/
                    },   
                    {
                    layout:'form',
                    xtype: 'fieldset',
                    title: 'Informações 2',
                    layout: 'form',
                    /*items:[
                        xtype: 'displayfield',
                        fieldLabel: 'Teste'
                    ]*/
                    }   
                    //this._getForm()
                ] 
                /*,
                items:[
                    {
                        xtype:'xtamplate'

                    }
                ]*/
                /*items: [this._getItens()],
                buttons:[
                    {
                        text:'Salvar',
                        handler: function()
                        {
                            this._minha({title:'titulo da funcao',valor:1500});
                        },
                        scope: this
                    }
                ]*/
                });

           
            return _panel;

        }

        
    }
);


toolkit.questionario.delete = function(grid, url, params)
{
    //console.debug(grid);
    var loading = new xt.LoadMask(grid.getEl(), {msg:'Por favor aguarde...', store:grid.getStore()});
    loading.show();
    Ext.Ajax.request({
        url:action(url),
        params: params,
        success:function(response, options)
        {

            loading.hide();
            json = Ext.decode(response.responseText);
            if(!json.success) 
                xAlert(json.msg);
            else 
                grid.getStore().reload();
        }
    });
}