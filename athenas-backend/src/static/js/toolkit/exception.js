/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

if(typeof(toolkit) != "undefiend") {

    toolkit.exception = { }

    toolkit.exception.Exception = function(message, type) {
        this.message = message;
        this.type    = (type != undefined ? type : "UnknowException");
    };

    toolkit.exception.Exception.prototype = {
        display: function() {
            var message = this.message;

            while(message.indexOf("<br/>") > 0)
                message = message.replace("<br/>", "\n");
            
            alert("Tipo da exceção:\n" + this.type + "\n---\n" + "Mensagem:\n" + message);
        }
    }

    toolkit.exception.JSONError = Ext.extend(
        toolkit.exception.Exception,
        {
            constructor: function(message) {
                toolkit.exception.JSONError.superclass.constructor.call(this, message, "Erro de negociação");
            }
        }
    );

    toolkit.exception.Permission = Ext.extend(
        toolkit.exception.Exception,
        {
            constructor: function(message) {
                toolkit.exception.Permission.superclass.constructor.call(this, message, "Sem permissão");
            }
        }
    );

    toolkit.exception.Bug = Ext.extend(
        toolkit.exception.Exception,
        {
            constructor: function(message) {
                toolkit.exception.Permission.superclass.constructor.call(this, message, "Falha no aplicativo");
            }
        }
    );

    toolkit.exception.CrudDelete = Ext.extend(
        toolkit.exception.Exception,
        {
            constructor: function(message) {
                toolkit.exception.Permission.superclass.constructor.call(this, message, "Erro deletando");
            }
        }
    );

    toolkit.exception.CrudSave = Ext.extend(
        toolkit.exception.Exception,
        {
            constructor: function(message) {
                toolkit.exception.Permission.superclass.constructor.call(this, message, "Erro gravando as modificações");
            }
        }
    );
}