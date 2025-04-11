Ext._define('rh.person.merge.Window', {
    extend: 'Ext.Window',

    static:{
        _route: {
            0: {
                id: 'chooseperson',
                handler: function(owner){
                    return owner.getChoosePerson({person: owner.person, windowCt: owner});
                },
                next: 1,
                previous: 0,
            },
            1: {
                id: 'naturalpersondata',
                next: 2,
                previous: 0,
                handler: function(owner){
                    return owner.getNaturalPersonData({person: owner.person, windowCt: owner});
                },
            },
            2: {
                id: 'sendpanel',
                next: undefined,
                previous: 1,
                handler: function(owner){
                    return owner.getSendPanel({person: owner.person, windowCt: owner});
                },
            }
        }
    },

    constructor: function(cfg){
        /*
         *@controller: nome do controller que conterá os métodos 'get_help_info' e 'get_help'
         *@cfg: configurações para o componente e para o window
         *  @@cache(true*|false): se as telas carregadas remotamente são cacheadas no componente
         *  @@actGetHelpInfo: nome do action no @controller que será chamado por _getHelpInfo
         *      return um json: {total: qtde_de_telas, @cfg,(items:[{id: }])}
         *
         *
         */
        cfg = core.nullValue(cfg, {});

        Ext.apply(cfg, {
            scope: this,
            title: 'Mesclar pessoas',
            layout:'card',
            activeItem: 0, // make sure the active item is set on the container config!
            width: 700,
            height: 600,
            autoScroll: true,
            id: 'merge',
            _gridArray: [],
            defaults: {
                autoScroll: true,
                bodyStyle: 'padding:15px',
                cls:'content-help',
                style: {
                    color: '#15428b'
                }
            },
            config:{
                remote: true,
                cache: true,
                total: 1,
                callback: function(){},
                actGetHelp: 'get_help_item',
                actGetHelpInfo: 'get_help_info'
            },
            bbar: [
                this.getPreviousBbar(),
                '->', // greedy spacer so that the buttons are aligned to each side
                this.getNextBbar()
            ],
            // items: [{
            //     id: 'passo-0',
            //     html: '<p style="text-align:center;"><img width="300" height="307" src="/' + global.Context + '/static/images/help/help_athenas_passo0.png" /></p>'
            // }],
            items: [
                this.getChoosePerson({person: cfg.person, windowCt: this}),
                // this.getNaturalPersonData({person: cfg.person, windowCt: this}),
            ],
            listeners:{
                scope: this,
                close: function(){
                    this.destroy();
                }
            }
        });
        rh.person.merge.Window.superclass.constructor.call(this, cfg);
    },

    _resetValues: function(){
        var route = this.static._route;
        var length = Object.keys(route).length;
        for (var i = 2; i < length; i++) {
            delete route[i];
        }
        this._gridArray = [];
    },

    addRoute: function(items){
        var scope = this;
        var route = this.static._route;
        var length = Object.keys(route).length;
        var last = this.static._route[length - 1];

        this._resetValues();

        length = Object.keys(route).length;
        var previous = length;
        var total = items.length + length + 1;

        items.forEach(function(item){
            // console.debug(item.data);
            var new_route = {
                id: 'genericgridct_' + item.name,
                next: total >= length ? length + 1 : length,
                previous: previous - 1,
                dataStore: item.data,
                fieldsStore: ['pk', 'unicode', 'person_unicode', 'config'],
                configOfTypeObj: item.config,
                columnsStore: [
                    {header: 'Chave', dataIndex:'pk'},
                    {header: 'Valor', dataIndex: 'unicode',id: 'autoExpandColumn', width: 260},
                    {header: 'Pessoa Física', dataIndex: 'person_unicode', width: 220},
                ],
                name: item.name,
                label: item.label,
                handler: function(owner){
                    return owner.getGenericGridContainer({
                        name: this.name,
                        title: this.label,
                        person: owner.person,
                        windowCt: owner,
                        data: this.dataStore,
                        fieldsStore: this.fieldsStore,
                        columnsStore: this.columnsStore,
                        configOfTypeObj: this.configOfTypeObj,
                    });
                }
            };
            route[length] = new_route;
            length += 1;
            previous += 1;
        });
        // console.debug(length);
        last.previous = length - 1;
        route[length] = last;
        // for (var i = 0; i < Object.keys(route).length; i++) {
        //     r = route[i];
        //     // console.debug(r);
        //     console.debug('pos: ' + i + ' # ' + r.previous + ' # ' + r.id + ' # ' + r.next);
        // }
    },

    getGridArray: function(){
        return this._gridArray;
    },

    getChoosePerson: function(cfg){
        if(!this._choosePerson)
            this._choosePerson = Ext._create('rh.person.merge.ChoosePersonPanel', cfg);
        return this._choosePerson;
    },

    getNaturalPersonData: function(cfg){
        this._naturalPersonData = Ext._create('rh.person.merge.NaturalPersonDataPanel', cfg);
        return this._naturalPersonData;
    },

    getGenericGridContainer: function(cfg){
        return Ext._create('rh.person.merge.GenericGridContainer', cfg);
    },

    getSendPanel: function(cfg){
        this._sendPanel = Ext._create('rh.person.merge.SendPanel', cfg);
        return this._sendPanel;
    },

    getPreviousBbar: function(cfg){
        if(!this._previousBbar){
            cfg = core.nullValue(cfg, {});
            Ext.apply(
                cfg,
                {
                    id: 'move-prev',
                    text: 'Anterior',
                    handler: this.navHandler.createDelegate(this, [-1]),
                    disabled: true
                }
            );
            this._previousBbar = cfg;
        }
        return this._previousBbar;
    },

    getNextBbar: function(cfg){
        if(!this._nextBbar){
            cfg = core.nullValue(cfg, {});
            Ext.apply(
                cfg,
                {
                    id: 'move-next',
                    text: 'Próximo',
                    handler: this.navHandler.createDelegate(this, [1])
                }
            );
            this._nextBbar = cfg;
        }
        return this._nextBbar;
    },

    getRoute: function(id){
        var route = {};
        this.static.map.foreach(function(item){
            // console.debug(item);
            if(item.get('id') == id)
                route = item;
        });
        return route;
    },

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
            scope._navToIndex(scope.items.length -1);
        }
    },
    _getHelpInfo: function(){
        /*
         */
        this._sendToRemote(this.config.controller, this.config.actGetHelpInfo, this.onGetHelpInfoSuccess);
    },

    _nav: function(index){
        var item = this.static._route[index];
        // console.debug(item);
        // console.debug(this);
        item = item.handler(this);
        // console.debug(item);
        if(item){
            this.add(item);
            // this.config.total = result.total+1;
        }
        this.layout.setActiveItem(index);
        // res = this._sendToRemote(this.config.controller, this.config.actGetHelp, this.onGetHelpSuccess, {'index':index})
        this._updateBbar();
    },

    _navToIndex: function(index){
        this.layout.setActiveItem(index);
        this._updateBbar();
    },

    navHandler: function(direction){
        var index = this.items.indexOfKey(this.layout.activeItem.id);
        // console.debug('navHandler direction ' + (index + direction));
        // console.debug('direction ' + direction);
        var active = this.layout.activeItem;
        // console.debug(active);
        // console.debug(this.items.length);
        // console.debug(this.config.total);
        // console.debug((index + direction + 1) > this.items.length);
        // console.debug(index + direction + 1);
        if((index + direction + 1) > this.items.length){
            this._nav(index + direction);
        }else{
            this._navToIndex(index + direction);
        }
        if(direction == -1){
            this.remove(active);
            active.destroy();
        }
        this.config.total += direction;
        this.config.total = this.config.total < 0 ? 1 : this.config.total;
    },

    _updateBbar: function(){
        var bbar = this.getBottomToolbar();
        var next = bbar.get('move-next');
        var prev = bbar.get('move-prev');
        var index = this.items.indexOfKey(this.layout.activeItem.id);
        // console.debug('_updateBbar index ' + index);
        if(index == this.config.total - 1 && index != 0){
            next.disable();
        }else if(index == 0){
            prev.disable();
        }else{
            next.enable();
            prev.enable();
        }
    }
});
