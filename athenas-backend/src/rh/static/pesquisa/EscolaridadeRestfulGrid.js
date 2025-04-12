/**
 *
 **/
Ext._define('rh.pesquisa.EscolaridadeRestfulGrid', {
    'extend': 'core.RestfulGrid',

    'restWindow': 'rh.pesquisa.EscolaridadeRestfulWindow',

    'keywordFieldMessage': 'Título',

    'getColumnModel': function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        dataIndex: 'servidor_unicode',
                        header: 'Servidor',
                        width: 200,
                        hidden: true
                    },
                    {
                        dataIndex:'nivel_escolaridade_display', 
                        header:'Nível de Escolaridade', 
                        width:285,
                        id: 'autoExpandColumn'
                    },
                    {
                        dataIndex:'instituicao', 
                        header:'Instituição', 
                        width:285
                    },
                    {
                        dataIndex:'curso', 
                        header:'Curso', 
                        width:285
                    },
                    {
                        dataIndex:'ano_conclusao', 
                        header:'Ano de Conclusão', 
                        width:100
                    },
                    {
                        dataIndex:'cidade_unicode', 
                        header:'Cidade', 
                        width:150
                    }
                ]
            );

        return this._columnModel;
    },

    'changeFitlerTipo': function(tipo) {
        if(tipo) {
            this.setFilterProperty('tipo', tipo, 0);
        }
        else
            this.removeFilterProperty('tipo');
    },

    'changeFilterPrincipal': function(enable) {
        if(enable)
            this.setFilterProperty('principal', true, 1);
        else
            this.removeFilterProperty('principal');
    },

    'filterServidor': function(){
         var wnd = Ext._create('Ext.Window', {
            'title': 'Selecionar Servidor',
            'modal': true,
            'resizable': false,
            'width': 450,
            'border': false,
            'buttons': [
                {
                    'text': 'Selecionar',
                    'scope': this,
                    'handler': function() {
                        var form = wnd.getComponent(0).getForm();

                        if(form.getValues().selecionado)
                            this.setFilterProperty('servidor', form.getValues().selecionado, 1002);
                        else
                            this.removeFilterProperty('servidor', 1002);

                        wnd.destroy();
                    }
                },
                {
                    'text': 'Fechar',
                    'scope': this,
                    'handler': function() {
                        wnd.destroy();
                    }
                }
            ],
            'items': Ext._create('Ext.form.FormPanel', {
                'frame': true,
                'items': [
                    {
                        'xtype': 'autocompletefield',
                        'fieldLabel': 'Servidor',
                        'hiddenName': 'selecionado',
                        'crudController': 'RHServidor',
                        'queryAction': 'query',
                        'queryParam': 'keyword',
                        'displayField': 'description',
                        'valueField': 'pk',
                        'width': 300,
                        'hideTrigger': true,
                        'emptyText': 'Insira a matrícula ou o nome do servidor'
                    }
                ]
            })
        }).show();

    },

    'toggleEscolaridade': function(tipo) {
        if(this._filterEscolaridade.indexOf(tipo) >= 0)
            this._filterEscolaridade.remove(tipo);
        else
            this._filterEscolaridade.push(tipo);

        this.setFilterProperty('nivel_escolaridade__in', this._filterEscolaridade, 1000);
    },

    'cleanFilter': function() {
        this._filterEscolaridade = [1, 2, 3, 4, 5, 6, 7];
        this.setFilter([
            {'property': 'nivel_escolaridade__in', 'value': this._filterEscolaridade, 'stage': 1000},
        ]);
    },

    'getFilterMenu': function() {
        if(!this._filterMenu)
            this._filterMenu = [
                {
                    'text': 'Por Servidor',
                    'scope':this,
                    'handler':this.filterServidor
                },
                '-',
                {
                    'text': 'Por Escolaridade',
                    'menu': [
                        {
                            'text': 'Médio',
                            'checked': true,
                            'scope': this,
                            'handler': function() { this.toggleEscolaridade(1) }
                        },
                        {
                            'text': 'Técnico',
                            'checked': true,
                            'scope': this,
                            'handler': function() { this.toggleEscolaridade(2) }
                        },
                        {
                            'text': 'Superior',
                            'checked': true,
                            'scope': this,
                            'handler': function() { this.toggleEscolaridade(3) }
                        },
                        {
                            'text': 'Pós-Graduação',
                            'checked': true,
                            'scope': this,
                            'handler': function() { this.toggleEscolaridade(4) }
                        },
                        {
                            'text': 'Mestrado',
                            'checked': true,
                            'scope': this,
                            'handler': function() { this.toggleEscolaridade(5) }
                        },
                        {
                            'text': 'Doutorado',
                            'checked': true,
                            'scope': this,
                            'handler': function() { this.toggleEscolaridade(6) }
                        },
                        {
                            'text': 'Pós-Doutorado',
                            'checked': true,
                            'scope': this,
                            'handler': function() { this.toggleEscolaridade(7) }
                        }
                    ]
                },
            ];

        return this._filterMenu;
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        rh.pesquisa.EscolaridadeRestfulGrid.superclass.constructor.call(this, cfg);

        this.cleanFilter()
        // this.setFilterProperty('data_baixa__isnull', true, -1000, false);
    }

})