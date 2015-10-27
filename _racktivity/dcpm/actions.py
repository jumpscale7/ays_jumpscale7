from JumpScale import j

ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):

    """
    process for install
    -------------------
    step1: prepare actions
    step2: check_requirements action
    step3: download files & copy on right location (hrd info is used)
    step4: configure action
    step5: check_uptime_local to see if process stops  (uses timeout $process.stop.timeout)
    step5b: if check uptime was true will do stop action and retry the check_uptime_local configureheck
    step5c: if check uptime was true even after stop will do halt action and retry the check_uptime_local check
    step6: use the info in the hrd to start the application
    step7: do check_uptime_local to see if process starts
    step7b: do monitor_local to see if package healthy installed & running
    step7c: do monitor_remote to see if package healthy installed & running, but this time test is done from central location
    """
    def prepare(self, serviceObj):
        j.system.platform.ubuntu.install('python-pygresql')

    def configure(self, serviceObj):
        j.system.fs.createDir('/etc/nginx/')
        j.system.fs.symlink('/etc/nginx/nginx.conf', '/opt/nginx/cfg/nginx.conf', overwriteTarget=True)
        j.system.fs.symlink('/etc/nginx/sites-available', '/opt/nginx/cfg/sites-available', overwriteTarget=True)
        j.system.fs.symlink('/etc/nginx/sites-enabled', '/opt/nginx/cfg/sites-enabled', overwriteTarget=True)
        j.system.fs.symlink('/opt/nginx/cfg/mime.types', '/etc/nginx/mime.types', overwriteTarget=True)

        j.system.fs.symlink('/etc/init.d/ays', '/etc/init.d/nginx', overwriteTarget=True)

        j.system.unix.addSystemUser('ftp')

        j.system.process.execute("pkill nginx", dieOnNonZeroExitCode=False)
        j.system.process.execute("/etc/init.d/rabbitmq-server restart")

        cmd = """
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
locale-gen en_US.UTF-8
sudo dpkg-reconfigure locales
        """
        j.system.process.execute(cmd)

        osisdb = """
[dcpm]
passwd = $(instance.param.dcpm.password)
login = dcpm
database = dcpmdb
ip = $(instance.param.postgresql.host)

[sequences]
sequences = {"racktivity": {"audit": {"id": "audit_id_seq"}, "values": {"id": "values_id_seq"}}}
        """

        j.system.fs.writeFile('/opt/qbase5/cfg/osisdb.cfg', osisdb)

        storelib2 = """
[main]
store = postgresql

[postgresql]
dbtype = postgresql
dbname = dcpmmon
username = dcpm
password = $(instance.param.dcpm.password)
hostname = $(instance.param.postgresql.host)
port = 5432
poolsize = 1
poolsize-applicationserver = 10
poolsize-workflowengine = 5

[sequences]
sequences = {"facts": {"dim_location": {"location_id": "location_id_seq"}, "dim_deviceinternal": {"deviceinternal_id": "deviceinternal_id_seq"}}}
        """
        j.system.fs.writeFile('/opt/qbase5/cfg/qconfig/storelib2.cfg', storelib2)

        cmds = ['chown -R syslog:adm /opt/qbase5/var/log/dcpm/',
                'rm -rf /opt/qbase5/lib/python/site-packages/pytz*',
                'apt-get install python-pip -y',
                'pip install --target=/opt/qbase5/lib/python/site-packages/ pytz',
                '/opt/qbase5/qshell -c "p.application.install(\'dcpm\')"']

        for cmd in cmds:
            j.system.process.execute(cmd)

        authjs = """
var Auth = {};

$(function() {
    var OAUTH_TOKEN = "oauth_token";
    var USER_NAME = "username";
    var REALM = "alkira";

    $("#loginInfo").append("<div id='logoutDiv' style='display:none;'><span id='loggeduser'>" +
        " </span>&nbsp;|&nbsp;<a href='#' id='logout' name='logout'>Log out</a>&nbsp;</div>");
    $("#loginInfo").append("<div id='loginDiv' style='display:none;'><a href='#' id='login' name='login'>Log in</a>" +
        "</div>");

    $('body').append("<div id='loginDialog' style='display:none;'>" +
        "<form name='login-form' id='login-form' method='get'>" +
        "<div><label for='username'>User name:</label><input type='text' name='username' id='username' " +
        "placeholder='username' class='input.text' /></div><div><label for='password'>Password:</label><input " +
        "type='password' name='password' id='password' placeholder='password' class='input.text' /></div><div><input " +
        "type='submit' name='login' id='login' value='Login' /></div></form></div>");

    function clearUserInfo() {
        localStorage.removeItem(OAUTH_TOKEN);
        localStorage.removeItem(USER_NAME);
    }

    function showLoginLink() {
        $("#logoutDiv").css("display", "none");
        $("#loginDiv").css("display", "inline");
    }

    function showLogoutLink() {
        $("#loginDiv").css("display", "none");
        $("#logoutDiv").css("display", "inline");
    }

    function showLoginDialog(event) {
        if (event) {
            event.preventDefault();
        }
        clearUserInfo();
        showLoginLink();
        $("#loginDialog").dialog({
            title: 'Log in',
            modal: true,
            width: 260,
            height:200,
            resizable: false
        });
        $("#loginDialog *:input[type!=hidden]:first").focus();
    }

    //Add the authentication info to the header of all Ajax request
    function addAuthenticationHeader(xhr, settings) {
        if (Auth.getFromLocalStorage(OAUTH_TOKEN) !== null) {
            var completeUrl;
            if (settings.url.charAt(0) === '/') {
                completeUrl = settings.url;
            } else {
                completeUrl = "/" + settings.url;
            }
            //remove the appname from the url
            if (completeUrl.indexOf("/" + LFW_CONFIG.appname) === 0) {
                completeUrl = completeUrl.substr(("/" + LFW_CONFIG.appname).length);
            }
            completeUrl = "http://" + REALM + completeUrl;

            var params = OAuth.getParameterMap(settings.data || ""); //convert to object
            //make sure our params are not in the url already
            var q = completeUrl.indexOf('?');
            if (q > 0) {
                var urlParams = OAuth.getParameterMap(completeUrl.substring(q + 1));
                var urlParam;
                for (urlParam in urlParams) {
                    if (urlParams.hasOwnProperty(urlParam) && params.hasOwnProperty(urlParam)) {
                        delete params[urlParam];
                    }
                }
            }

            var accessor = {
                    consumerSecret: "",
                    tokenSecret: ""
                },
                message = {
                    action: completeUrl,
                    method: settings.type,
                    parameters: params
                };
            var token = Auth.getFromLocalStorage(OAUTH_TOKEN);
            if (token !== null) {
                var parts = token.token.split("&");
                if (parts.length === 2) {
                    var firstPart   = parts[0];
                    var secondPart  = parts[1];
                    if (firstPart.split("=")[0] === "oauth_token") {
                        message.parameters.oauth_token = "token_$(" + firstPart.split("=")[1] + ")";
                        accessor.token = message.parameters.oauth_token;
                        accessor.tokenSecret = secondPart.split("=")[1];
                    } else {
                        message.parameters.oauth_token = "token_$(" + secondPart.split("=")[1] + ")";
                        accessor.token = message.parameters.oauth_token;
                        accessor.tokenSecret = firstPart.split("=")[1];
                    }
                }
            }

            message.parameters.oauth_verifier = "";
            message.parameters.oauth_consumer_key = Auth.getFromLocalStorage(USER_NAME);
            accessor.consumerKey = message.parameters.oauth_consumer_key;
            OAuth.setTimestampAndNonce(message);
            OAuth.SignatureMethod.sign(message, accessor);

            //form the OAuth header
            var oauthParams = {
                oauth_consumer_key: message.parameters.oauth_consumer_key,
                oauth_token: message.parameters.oauth_token,
                oauth_verifier: message.parameters.oauth_verifier,
                oauth_nonce: message.parameters.oauth_nonce,
                oauth_timestamp: message.parameters.oauth_timestamp,
                oauth_signature: message.parameters.oauth_signature,
                oauth_signature_method: message.parameters.oauth_signature_method
            };

            xhr.setRequestHeader("authorization", OAuth.getAuthorizationHeader(REALM, oauthParams));
        }
        else {
            showLoginLink();
        }
    }

    function displayUser() {
        var username = Auth.getFromLocalStorage(USER_NAME);
        if (username !== null) {
            showLogoutLink();
            $("#loggeduser", "#loginInfo").html(username);
        }
    }

    function addToLocalStorage(key, value) {
        //The local storage entry is valid for 1 hour
        var data = {timestamp: new Date().getTime() + (60*60*1000), value: value};
        localStorage.setItem(key,  JSON.stringify(data));
    }

    //Token generation function
    function makeOAuthRequest(username, password) {
        var url = LFW_CONFIG.uris.oauthservice;


        jQuery.ajax({
            type: "POST",
            url: url,
            data: {'user': username, 'password': password},
            error: function(xhr, text, exc, options) {
                $("#loginDialog").find("input").attr("disabled", false);
                $.alerterror(xhr, text, exc, options);
            },
            success: function(data) {
                Auth.parseOAuthToken(data, username);
            }
        });
    }

    Auth.getFromLocalStorage = function(key) {
        var itemJson = localStorage.getItem(key);
        if (!itemJson) {
            return null;
        }
        var item = $.parseJSON(itemJson);
        var now = new Date().getTime().toString();
        if (item === null) {
            return null;
        }

        return item.value;
    };

    Auth.parseOAuthToken = function(token, username, noreload) {
        if (token.error) {
            $.alert(token.message, {title: 'Invalid login'});
            $("#loginDialog").find("input").attr("disabled", false);
            return;
        }

        addToLocalStorage(OAUTH_TOKEN, token);
        showLogoutLink();
        $("#loginInfo #loggeduser").html(username);
        addToLocalStorage(USER_NAME, username);
        $("#loginDialog").dialog("close")
                         .find("input").attr("disabled", false);
        if (!noreload) {
            window.location.reload();
        }
    };

    Auth.getOAuthUrlParams = function(url) {
        var completeUrl = url;
        //remove the appname from the url
        if (completeUrl.indexOf("/" + LFW_CONFIG.appname) === 0) {
            completeUrl = completeUrl.substr(("/" + LFW_CONFIG.appname).length);
        }
        completeUrl = "http://" + REALM + completeUrl;

        var params = OAuth.getParameterMap(""); //convert to object
        //make sure our params are not in the url already
        var q = completeUrl.indexOf('?');
        if (q > 0) {
            var urlParams = OAuth.getParameterMap(completeUrl.substring(q + 1));
            var urlParam;
            for (urlParam in urlParams) {
                if (urlParams.hasOwnProperty(urlParam) && params.hasOwnProperty(urlParam)) {
                    delete params[urlParam];
                }
            }
        }

        var accessor = {
                consumerSecret: "",
                tokenSecret: ""
            },
            message = {
                action: completeUrl,
                method: "GET",
                parameters: params
            };
        var token = Auth.getFromLocalStorage(OAUTH_TOKEN);
        if (token !== null) {
            var parts = token.split("&");
            if (parts.length === 2) {
                var firstPart   = parts[0];
                var secondPart  = parts[1];
                if (firstPart.split("=")[0] === "oauth_token") {
                    message.parameters.oauth_token = "token_$(" + firstPart.split("=")[1] + ")";
                    accessor.token = message.parameters.oauth_token;
                    accessor.tokenSecret = secondPart.split("=")[1];
                } else {
                    message.parameters.oauth_token = "token_$(" + secondPart.split("=")[1] + ")";
                    accessor.token = message.parameters.oauth_token;
                    accessor.tokenSecret = firstPart.split("=")[1];
                }
            }
        }

        message.parameters.oauth_verifier = "";
        message.parameters.oauth_consumer_key = Auth.getFromLocalStorage(USER_NAME);
        accessor.consumerKey = message.parameters.oauth_consumer_key;
        OAuth.setTimestampAndNonce(message);
        OAuth.SignatureMethod.sign(message, accessor);

        //form the OAuth header
        var oauthParams = {
            oauth_consumer_key: message.parameters.oauth_consumer_key,
            oauth_token: message.parameters.oauth_token,
            oauth_verifier: message.parameters.oauth_verifier,
            oauth_nonce: message.parameters.oauth_nonce,
            oauth_timestamp: message.parameters.oauth_timestamp,
            oauth_signature: message.parameters.oauth_signature,
            oauth_signature_method: message.parameters.oauth_signature_method
        };

        var header = 'realm=' + OAuth.percentEncode(REALM);
        var list = OAuth.getParameterList(oauthParams);
        var p = 0;
        for (p = 0; p < list.length; ++p) {
            var parameter = list[p];
            var name = parameter[0];
            if (name.indexOf("oauth_") === 0) {
                header += '&' + OAuth.percentEncode(name) + '=' + OAuth.percentEncode(parameter[1]);
            }
        }
        return header;
    };

    $("#login", "#loginInfo").click(showLoginDialog);

    $("#logout", "#loginInfo").click(function(event) {
        event.preventDefault();
        clearUserInfo();
        window.location = "/" + LFW_CONFIG.appname + "/";
    });

    $("#login", "#loginDialog").click(function(event) {
        event.preventDefault();
        if (jQuery.trim( $('#username').val() ) === "" || jQuery.trim( $('#password').val() ) === "") {
            $.alert("Invalid username/password combination!", {title: "Invalid Login"});
            return;
        }
        $("#loginDialog").find("input").attr("disabled", true);
        makeOAuthRequest($('#username').val(), $('#password').val());
    });

    //Install global error handler so we can show a login box if required but only if we got it from the rest api
    //from the applicationserver
    $(document).ajaxError(function(event, xhr, options) {
        if ((xhr.status === 403 || xhr.status === 401) &&
            options.url.indexOf(LFW_CONFIG.appname + "/appserver/rest/") !== -1) {
            var responseDate = new Date(xhr.getResponseHeader('Date')),
                localDate = new Date(),
                dateDiff = Math.abs(responseDate - localDate)/1000;
            event.preventDefault();
            if (dateDiff>60) {
                var msg = "Your time differs from server time for more than one minute, this may cause problems logging in";
                $.confirm(msg, {title:'Warning', ok: showLoginDialog});
            } else {
                showLoginDialog();
            }
        } else if (xhr.status === 405) {
            event.preventDefault();
            if (localStorage.getItem(USER_NAME) === null) {
                if (LFW_CONFIG.isconfigured) {
                    showLoginDialog();
                }
            } else {
                if (options.redirect) {
                    window.location.replace('#/View/Unauthorized');
                }
            }
        }
    });

    //Intercept all Ajax requests to add the OAuth header parameters if any
    $(document).ajaxSend(function(event, xhr, settings) {
        addAuthenticationHeader(xhr, settings);
    });

    displayUser();
});
        """

        j.system.fs.writeFile('/opt/qbase5/pyapps/dcpm/portal/static/js/oauth.js', authjs)
        j.system.process.execute('/opt/qbase5/qshell -c "p.application.restart(\'dcpm\')"')

        # print "Please install DCPM app in qbase by executing:\n/opt/qbase5/qshell -c \"p.application.install('dcpm')\""
